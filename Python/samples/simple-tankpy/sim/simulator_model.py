from sim.tankcontroller import TankController
from typing import NamedTuple, Dict, Any

class SimulatorModel:

    def __init__(self):
        """ Perform global initialization here if needed before running episodes. """
        pass

    def reset(self, config) -> Dict[str, Any]:
        """ Reset any state from the previous episode and get ready to start a new episode. """
        self.tc = TankController(config['hSetPoint'], config['initialFlow'])
        return { 'sim_halted': False, 
                'hLiq': self.tc.blt.hLiq,
                'overflow': self.tc.blt.overflowed} # added the dict to this file

    def step(self, action) -> Dict[str, Any]:
        """ Apply the specified action and perform one simulation step. """
        self.tc.step(action['flowrate'])
        # If 'sim_halted' is set to True, that indicates that the simulator is unable to continue and
        # the episode will be discarded. This simulator sets it to False becasue it can always continue.
        return { 'sim_halted': False, 
                'hLiq': self.tc.blt.hLiq,
                'overflow': self.tc.blt.overflowed}
