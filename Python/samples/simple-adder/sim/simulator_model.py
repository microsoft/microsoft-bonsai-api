from sim.adder import Adder
from typing import NamedTuple, Dict, Any

class SimulatorModel:
    class SimStatus(NamedTuple):
        halted: bool
        state: Dict[str, Any]

    def __init__(self):
        pass

    def reset(self, config) -> SimStatus:
        self.adder = Adder(config['initial_value'])
        return self.SimStatus(False, { 'value': self.adder.value })

    def step(self, action) -> SimStatus:
        self.adder.add(action['addend'])
        return self.SimStatus(False, { 'value': self.adder.value })
