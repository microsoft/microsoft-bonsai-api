from sim.cartpole import CartPole
from typing import NamedTuple, Dict, Any

class SimulatorModel:
    """
    Manages the CartPole that represents the simulation for this sample.
    Implements the reset and step methods required for a Bonsai simulator.
    """

    def __init__(self):
        """ Perform global initialization here if needed before running episodes. """
        self.cartpole = CartPole()

    def reset(self, config) -> Dict[str, Any]:
        """ Reset any state from the previous episode and get ready to start a new episode. """
        self.cartpole.reset(**config)
        state = self.cartpole.state.copy()
        state['sim_halted'] = False
        return state
    
    def step(self, action) -> Dict[str, Any]:
        """ Apply the specified action and perform one simulation step. """
        self.cartpole.step(action['command'])
        state = self.cartpole.state.copy()
        state['sim_halted'] = False
        return state
