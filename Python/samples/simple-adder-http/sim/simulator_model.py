import requests
from typing import NamedTuple, Dict, Any

class SimulatorModel:
    """
    Manages the Adder that represents the simulation for this sample.
    Implements the reset and step methods required for a Bonsai simulator.
    """

    def __init__(self):
        """ Perform global initialization here if needed before running episodes. """
        pass

    def reset(self, config) -> Dict[str, Any]:
        """ Reset any state from the previous episode and get ready to start a new episode. """
        # self.adder = Adder(config['initial_value'])
        res = requests.post('http://localhost:21000/reset', json=config) 
  
        # Convert response data to json
        return_dict = {'sim_halted': False}
        return_dict.update(res.json())
        
        return return_dict

    def step(self, action) -> Dict[str, Any]:
        """ Apply the specified action and perform one simulation step. """
        # self.adder.add(action['addend'])
        res = requests.post('http://localhost:21000/step', json=action) 
  
        # Convert response data to json
        return_dict = {'sim_halted': False}
        return_dict.update(res.json())
        # If 'sim_halted' is set to True, that indicates that the simulator is unable to continue and
        # the episode will be discarded. This simulator sets it to False becasue it can always continue.
        return return_dict
    
 
