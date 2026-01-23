import simpy, random
from statistics import mean
from tqdm import tqdm

from .node.node import Node
from .core.network import Network

from .core.energy_logger import EnergyLogger

from .config import NODES, SIM_TIME, RANGE

def main():
    env = simpy.Environment()
    nodes = [Node(env, i, random.uniform(0,RANGE), random.uniform(0,RANGE)) for i in range(NODES)]

    chunk_size = SIM_TIME // 20 
    with tqdm(total=SIM_TIME, desc="Simulating", unit="time") as pbar:
        for t in range(0, SIM_TIME, chunk_size):
            env.run(until=min(t + chunk_size, SIM_TIME))
            pbar.update(chunk_size)

    kpis = [n.kpi.get_disc_kpis(n.neighbors) for n in nodes]

    e_per_cycle, avg_time, avg_success = [mean(metric) for metric in zip(*kpis)]
    success_disc_e = mean([n.kpi.get_success_disc_e() for n in nodes])

    print(f"Energy usage per DISC cycle: {e_per_cycle} J")
    print(f"Time till first DISC receive: {avg_time} sec")
    print(f"Energy per successfull DISC cycle: {success_disc_e} J")
    print(f"DISC success rate: {avg_success} %")

    sync_tries = [
        n.sync_tries
        for n in nodes
    ]
    avg_syncs = mean(sync_tries)
    print("Avg SYNCs sent:", avg_syncs)

    acks_list = [
        n.acks_received
        for n in nodes
    ]
    avg_acks = mean(acks_list)
    print("Avg ACKs received:", avg_acks)

    print("Sync success rate:", (sum(acks_list) / sum(sync_tries) * 100) if avg_syncs > 0 else 0, "%")

    EnergyLogger.plot()

if __name__ == "__main__":
    main()