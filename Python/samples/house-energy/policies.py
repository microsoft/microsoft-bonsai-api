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


def coast(state):
    """
    Ignore the state, go straight.
    """
    action = {"hvacON": 1}
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


POLICIES = {"random": random_policy, "coast": coast, "P_controller": P_controller}

