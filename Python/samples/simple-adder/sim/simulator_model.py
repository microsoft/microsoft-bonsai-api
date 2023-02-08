from sim.adder import Adder
from typing import NamedTuple, Dict, Any

class SimulatorModel:
    """
    Manages the Adder that represents the simulation for this sample.
    Implements the reset and step methods required for a Bonsai simulator.
    """

    def __init__(self):
        """ Perform global initialization here if needed before running episodes. """
        self.sim_name = "simple-adder"

    def reset(self, config) -> Dict[str, Any]:
        """ Reset any state from the previous episode and get ready to start a new episode. """
        self.adder = Adder(config['initial_value'])
        return { 'sim_halted': False, 'value': self.adder.value }

    def step(self, action) -> Dict[str, Any]:
        """ Apply the specified action and perform one simulation step. """
        self.adder.add(action['addend'])
        # If 'sim_halted' is set to True, that indicates that the simulator is unable to continue and
        # the episode will be discarded. This simulator sets it to False becasue it can always continue.
        return { 'sim_halted': False, 'value': self.adder.value }
