import simpy, random, math

from ..core.network import Network
from ..core.energy_logger import EnergyLogger
from .capacitor import Capacitor

from .mode import Mode
from .packet import Packet

from ..config import *

class Node:
    def __init__(self, env: simpy.Environment, id: int, x: float, y: float):
        self.env = env
        self.id = id
        self.x, self.y = x, y

        self.mode: Mode = Mode.IDLE
        self.capacitor = Capacitor(id)
        self.clock_drift = random.uniform(*CLOCK_DRIFT_MULTIPLIER_RANGE)

        self.neighbors: dict[int, list[tuple[int, int]]]= {}

        self.listen_time = 0
        self.listen_process = None

        self.is_sync = False
        self.sync_tries = 0
        self.acks_received = 0

        Network().register_node(self)
        self.env.process(self.run())

    def run(self):
        while True:
            EnergyLogger().log(self.id, self._local_time(), self.capacitor.energy)

            # Discovery part
            listen_time = math.ceil(random.uniform(*DISC_LISTEN_RANGE))
            energy_to_use = listen_time * E_RECEIVE + E_TX * 2 + E_RX * 2

            # Sync part
            energy_for_sync = SYNC_LISTEN_TIME * E_RECEIVE + E_TX + E_RX
            idle_time_for_sync = self.capacitor.time_to_charge_to(energy_for_sync)
            (sync_with, sync_in) = self._soonest_sync()

            # Pick what's sooner and prioritize
            if sync_with != -1 and sync_in >= idle_time_for_sync and sync_in - idle_time_for_sync < SYNC_PREPARATION_TIME:
                self.is_sync = True
                listen_time = SYNC_LISTEN_TIME
                energy_to_use = energy_for_sync
                idle_time = sync_in
            else:
                self.is_sync = False
                idle_time = self.capacitor.time_to_charge_to(energy_to_use)

            self.listen_time = listen_time
            idle_time = math.floor(idle_time)

            yield self.env.timeout(idle_time)
            self.capacitor.harvest(idle_time)

            EnergyLogger().log(self.id, self._local_time(), self.capacitor.energy)

            if self.capacitor.remaining_energy() >= energy_to_use:
                listen_duration = random.uniform(*SYNC_TIME_RANGE) if self.is_sync else (listen_time / 2)
                listen_duration = math.floor(listen_duration)
                
                # First listen
                self.listen_process = self.env.process(self.enable_receiving(listen_duration))
                heard = False
                try:
                    yield self.listen_process
                    heard = self.listen_process.value
                except simpy.Interrupt:
                    pass
                finally:
                    self.listen_process = None
                
                # Transmit if nothing heard
                if not heard:
                    yield self.env.process(
                        self.transmit(
                            Packet.SYNC if self.is_sync else Packet.DISC,
                            sync_with if self.is_sync else None
                        )
                    )
                
                # Second listen
                remaining_time = listen_time - listen_duration
                self.listen_process = self.env.process(self.enable_receiving(remaining_time))
                try:
                    yield self.listen_process
                except simpy.Interrupt:
                    pass
                finally:
                    self.listen_process = None

            self.mode = Mode.IDLE

    def enable_receiving(self, duration: int):
        available_time = math.floor(self.capacitor.remaining_energy() / E_RECEIVE)
        energy_to_use = E_RECEIVE * min(duration, available_time)

        if self.capacitor.remaining_energy() < energy_to_use:
            return False

        self.mode = Mode.RECEIVE
        self.capacitor.discharge(energy_to_use)        
        yield self.env.timeout(available_time)
        self.mode = Mode.IDLE

        # ! Returns True even if it heard the packet it has not expected for
        return len(Network().messages_received_from(self)) > 0

    def transmit(self, packet: Packet, to: int | None):
        if self.capacitor.remaining_energy() < E_TX:
            return False
               
        self.mode = Mode.TRANSMIT
        self.capacitor.discharge(E_TX)
        yield self.env.timeout(PT_TIME)
        self.mode = Mode.RECEIVE

        if packet == Packet.SYNC:
            self.sync_tries += 1

        msg = {
            'type': packet,
            'from': self.id,
            'to': to,
            'time': self._local_time()
        }

        yield self.env.process(Network.broadcast(self, msg))
        return True

    def receive(self, msg: dict):
        if self.mode != Mode.RECEIVE or self.capacitor.remaining_energy() < E_RX:
            return False

        self.mode = Mode.DECODE
        self.capacitor.discharge(E_RX)
        yield self.env.timeout(PT_TIME)
        self.mode = Mode.RECEIVE

        type = Packet(msg['type'])
        sender = msg['from']
        receiver = msg['to']
        sender_time = msg['time']

        (_, time_to_meet) = self._soonest_sync(sender)

        if(receiver != None and receiver != self.id):
            return

        if type == Packet.DISC and not self.is_sync: # only this has sender to None
            if(self.neighbors.get(sender) == None or time_to_meet < 0):
                yield self.env.process(self.transmit(Packet.DISC_ACK, sender))
        elif type == Packet.DISC_ACK:
            self._add_meeting(sender, sender_time)
            yield self.env.process(self.transmit(Packet.DISC_ACK_2, sender))
        elif type == Packet.DISC_ACK_2:
            self._add_meeting(sender, sender_time)
        elif type == Packet.SYNC:
            self._add_meeting(sender, sender_time)
            yield self.env.process(self.transmit(Packet.SYNC_ACK, sender))
            if self.listen_process:
                self.listen_process.interrupt('sync_received')
        elif type == Packet.SYNC_ACK:
            self._add_meeting(sender, sender_time)
            self.acks_received += 1
            if self.listen_process:
                self.listen_process.interrupt('ack_received')
    
    def _soonest_sync(self, node_id: int = -1) -> tuple[int, float]:
        """
        Calculates the next meeting with node based on current timestamp and SYNC_INTERVAL
        Returns infinite in case there are no neighbours
        """
        soonest_meet = float('inf')
        soonest_meet_with = -1

        for id, neigh in self.neighbors.items():
            if not neigh:
                continue
                
            drift_rate = self._estimate_drift(id)
            
            if drift_rate == 0:
                continue
                
            meet_at_timestamp = neigh[0][0] / drift_rate + 1 + SYNC_LISTEN_TIME / 2
            meet_in = meet_at_timestamp - self._local_time()

            if node_id == id:
                return (node_id, math.floor(meet_in))

            if meet_in > 0 and meet_in < soonest_meet:
                soonest_meet = meet_in
                soonest_meet_with = id

        if soonest_meet_with == -1:
            return (-1, float('inf'))
        
        return (soonest_meet_with, math.floor(soonest_meet))

    def _local_time(self) -> int:
        """
        Return local timestamp of the node based on its clock drift
        """
        return math.floor(self.env.now * self.clock_drift)
    
    def _add_meeting(self, sender_id: int, sender_time: int):
        """
        Adds meeting to a list of meeting with a different node
        Later used to estimate drift
        """
        neighbor = self.neighbors.get(sender_id)

        if neighbor == None:
            neighbor = []
            self.neighbors[sender_id] = neighbor
        
        neighbor.append((self._local_time(), sender_time))
        
        if len(neighbor) > 8:
            neighbor.pop(0)
    
    def _estimate_drift(self, id: int) -> float:
        """
        Calculates drift of current node in respect ot the node with another id
        Using linear regression
        """
        points = self.neighbors[id]
        if len(points) < 2:
            return 1.0
        
        n = len(points)
        sum_x = sum(p[0] for p in points)
        sum_y = sum(p[1] for p in points)
        sum_xy = sum(p[0] * p[1] for p in points)
        sum_xx = sum(p[0] ** 2 for p in points)
        
        denominator = n * sum_xx - sum_x ** 2
        if denominator == 0:
            return 1.0
        
        drift_rate = (n * sum_xy - sum_x * sum_y) / denominator
        
        if drift_rate <= 0 or drift_rate > 2.0:
            return 1.0
        
        return drift_rate