from ..config import *

class KPI:
    def __init__(self):
        self.e_total = 0
        self.disc_start_time = 0
        self.disc_first_time = 0
    
        self.disc_e_send = 0
        self.disc_sent = 0
        self.disc_e_receive = 0
        self.disc_received = 0

        self.disc_success_e = 0
        self.disc_suceessfull = 0

        self.sync_sent = 0
        self.acks_received = 0

    def add_e(self, energy):
        self.e_total += energy

    def start_discovery(self, local_time):
        if self.disc_start_time == 0:
            self.disc_start_time = local_time

    def send_discovery(self, listen_time):
        self.disc_sent += 1

        listen_e = listen_time * E_RECEIVE
        self.disc_e_send += listen_e + E_TX
        self.disc_e_receive += listen_e

    def receive_discovery(self, listen_time, local_time):
        self.disc_received += 1
        self.disc_e_receive += listen_time / 2 * E_RECEIVE + E_RX

        if self.disc_first_time == 0:
            self.disc_first_time = local_time

    def receive_disc_ack(self, listen_time):
        self.disc_suceessfull += 1
        self.disc_success_e += listen_time * E_RECEIVE + E_TX + E_RX

    def get_success_disc_e(self):
        return self.disc_success_e / self.disc_suceessfull

    def get_disc_kpis(self, neigbors):
        e_per_cycle = (self.disc_e_receive + self.disc_e_send) / (self.disc_sent + self.disc_received)

        time_till_success = (self.disc_first_time - self.disc_start_time) / 1_000
        success_rate = len(neigbors) / (NODES - 1) * 100

        return (e_per_cycle, time_till_success, success_rate)