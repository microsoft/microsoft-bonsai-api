"""
Fixed policies to test our sim integration with. These are intended to take
Brain states and return Brain actions.
"""

import random
from typing import Dict
import requests

global available_policy_list
available_policy_list = ["move_right",
                         "move_left",
                         "move_up",
                         "move_down",
                         "do_nothing"]
def chosen_policy(state, policy_name="move_right"):
    """
    Apply selected user policy.
    """
    
    # Ignore the state, go right.
    if policy_name == "move_right":
        action = {"engine1": 0, "engine2": 1}
    # Ignore the state, go left.
    elif policy_name == "move_left":
        action = {"engine1": 0, "engine2": -1}
    # Ignore the state, go up.
    elif policy_name == "move_up":
        action = {"engine1": 1, "engine2": 0}
    # Ignore the state, go down.
    elif policy_name == "move_down":
        action = {"engine1": -1, "engine2": 0}
    # Ignore the state, fo nothing.
    elif policy_name == "do_nothing":
        action = {"engine1": 0, "engine2": 0}
    
    return action


def brain_policy(
    state: Dict[str, float], exported_brain_url: str = "http://localhost:5000"
):

    prediction_endpoint = f"{exported_brain_url}/v1/prediction"
    response = requests.get(prediction_endpoint, json=state)

    return response.json()
