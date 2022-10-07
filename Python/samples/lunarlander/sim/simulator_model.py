from LunarLander import LunarLander
from typing import NamedTuple, Dict, Any, Union


class SimulatorModel:
    """
    Manages the LunarLander model that represents the simulation for this sample.
    Implements the reset and step methods required for a Bonsai simulator.
    """

    def __init__(self,
        render: bool = False,
        log_data: Union[bool, str] = False,
        debug: bool = True,):
        """ Perform global initialization here if needed before running episodes. """

        # render functionality
        self.render = render
        # logging features
        self.log_data = log_data
        # debug functionality
        self.debug = debug

        # initialize sim
        self.sim = LunarLander(render = self.render,
                               log_data = self.log_data, # Data disabled since it is taken care by this class.
                               debug = self.debug)
        
        pass

    def reset(self, config) -> Dict[str, Any]:
        """ Reset any state from the previous episode and get ready to start a new episode. """
        self.sim = LunarLander(render = self.render,
                               log_data = self.log_data, # Data disabled since it is taken care by this class.
                               debug = self.debug)
                
        # Start simulation.
        self.sim.episode_start(config)

        return self.sim.get_state()                        

    def step(self, action) -> Dict[str, Any]:
        """ Apply the specified action and perform one simulation step. """
        # Apply action to sim.
        self.sim.episode_step(action)

        # If 'sim_halted' is set to True, that indicates that the simulator is unable to continue and
        # the episode will be discarded. This simulator sets it to False because it can always continue.
        return self.sim.get_state()

