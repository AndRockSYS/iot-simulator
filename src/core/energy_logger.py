import matplotlib.pyplot as plt
from collections import defaultdict
import math

from ..config import *

class EnergyLogger:
    enabled = True
    data = defaultdict(list)

    @classmethod
    def log(cls, node_id, time, energy):
        if cls.enabled:
            cls.data[node_id].append((time, energy))

    @classmethod
    def disable(cls):
        cls.enabled = False

    @classmethod
    def plot(cls, filename="energy_plot.png"):
        if not cls.enabled:
            return

        if SIM_TIME >= ONE_DAY:
            time_divisor = ONE_DAY
            time_unit = "days"
        elif SIM_TIME >= ONE_DAY / 24:
            time_divisor = ONE_DAY / 24
            time_unit = "hours"
        else:
            time_divisor = 1000
            time_unit = "seconds"

        width = math.floor(SIM_TIME / ONE_DAY)
        plt.figure(figsize=(min(max(20, width * 30), 150), 7.5))
        
        max_energy = 0
        for node_id, records in cls.data.items():
            times, energies = zip(*records)
            max_energy = max(max_energy, max(energies))
            times_converted = [t / time_divisor for t in times]
            plt.plot(times_converted, energies, label=f"Node {node_id}")

        y_upper = max(max_energy * 1.15, E_TRESHOLD * 1.1)
        plt.ylim(0, y_upper)

        plt.axhline(y=E_TRESHOLD, color='black', linestyle='--', linewidth=1.5, label='Threshold')
        if E_MAX <= y_upper:
            plt.axhline(y=E_MAX, color='black', linestyle='--', linewidth=1.5, label='Max')

        plt.xlabel(f"Time ({time_unit})")
        plt.ylabel("Energy (joules)")
        plt.title("Energy during Simulation")
        plt.legend(loc='upper left', fontsize='small', ncol=2)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(filename)