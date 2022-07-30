from sim.newsvendor import NewsvendorEnv
from typing import NamedTuple, Dict, Any

class SimulatorModel:
    def __init__(self):
        """ Perform global initialization here if needed before running episodes. """
        pass

    def reset(self, config) -> Dict[str, Any]:
        """ Reset any state from the previous episode and get ready to start a new episode. """
        self.newsvendor = NewsvendorEnv()
        return ({"state1" : self.newsvendor.state.tolist(), "reward1" : 0.0, "sim_halted": False})


    def step(self, action) -> Dict[str, Any]:

        state, reward, done, _ = self.newsvendor.step(action['amountToOrder'])
        # If 'sim_halted' is set to True, that indicates that the simulator is unable to continue and
        # the episode will be discarded. This simulator sets it to False because it can always continue.
        return ({"state1" : state.tolist(), "reward1" : float(reward), "sim_halted": done})
    