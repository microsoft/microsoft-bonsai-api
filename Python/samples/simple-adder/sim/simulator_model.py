from typing import NamedTuple, Dict, Any

class SimulatorModel:
    class SimStatus(NamedTuple):
        halted: bool
        state: Dict[str, Any]

    def __init__(self):
        pass

    def reset(self, config) -> SimStatus:
        self.value = config['initial_value']
        return self.SimStatus(False, { 'value': self.value })

    def step(self, action) -> SimStatus:
        self.value += action['addend']
        return self.SimStatus(False, { 'value': self.value })
