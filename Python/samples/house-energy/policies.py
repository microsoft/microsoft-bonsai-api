"""
Fixed policies to test our sim integration with. These are intended to take
Brain states and return Brain actions.
"""

import random
from typing import Dict


def random_policy(state: Dict = None):
    """
    Ignore the state, move randomly.
    """
    action = {"hvacON": random.randint(0, 1)}
    return action

def P_controller(state):
    """
    Use only the temperature desired - actual to generate hvac ON or OFF requests
    """
    Kp = 0.2
    output = Kp * (state["Tset"] - state["Tin"])
    if output < 0:
        control = 1
    else:
        control = 0
    action = {"hvacON": control}
    return action

def brain_policy(
    state: Dict[str, float], exported_brain_url: str = "http://localhost:5000"
):

    prediction_endpoint = f"{exported_brain_url}/v1/prediction"
    response = requests.get(prediction_endpoint, json=state)

    return response.json()

def forget_memory(
    url: str = "http://localhost:5000/v1"
):
    # Reset the Memory vector because exported brains don't understand episodes 
    response = requests.delete(url)
    if response.status_code == 204:
        print('Resetting Memory vector in exported brain...')
    else:
       print('Error: {}'.format(response.status_code)) 

