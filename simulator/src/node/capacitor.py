import random, math

from ..config import *

class Capacitor:
    lux_level = 0
    energy = 0

    def __init__(self, id: int):
        range = LOW_LIGHT_RANGE_LUX if id < LOW_POWERED_NODES else HIGH_LIGHT_RANGE_LUX

        self.lux_level = random.uniform(*range)
        self.lux_level = math.floor(self.lux_level)

    def harvest_rate(self):
        harvest_rate = (0.9083 * self.lux_level - 9.2714) / 10 ** 6 / 1_000
        return harvest_rate
            
    def harvest(self, time: int):
        self.energy = min(self.energy + self.harvest_rate() * time, E_MAX)

    def discharge(self, joules: float):
        if joules > self.remaining_energy():
            raise ValueError("Not enough energy to use")
        self.energy -= joules

    def time_to_charge_to(self, joules: float):
        miliseconds = (joules - self.remaining_energy()) / self.harvest_rate()
        return math.ceil(miliseconds)

    def remaining_energy(self):
        return max(0, self.energy - E_TRESHOLD)
    
