"""
Fixed policies to test our sim integration with. These are intended to take
Brain states and return Brain actions.
"""

import random
from typing import Dict
from exported_brain_interface import ExportedBrainPredictor
import requests


def random_policy(state):
    """
    Ignore the state, move randomly.
    """
    action = {"command": random.randint(0, 1)}
    return action


def coast(state):
    """
    Ignore the state, go straight.
    """
    action = {"command": 1}
    return action


def brain_policy(
    state: Dict[str, float], exported_brain_url: str = "http://localhost:5000"
):

    prediction_endpoint = f"{exported_brain_url}/v1/prediction"
    response = requests.get(prediction_endpoint, json=state)

    return response.json()


POLICIES = {"random": random_policy, "coast": coast}

