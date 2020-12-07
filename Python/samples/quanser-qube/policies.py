"""
Fixed policies to test our sim integration with. These are intended to take
Brain states and return Brain actions.
"""

import random
import numpy as np


def random_policy(state):
    """
    Ignore the state, move randomly.
    """
    action = {"Vm": random.uniform(-3, 3)}
    return action


def coast(state):
    """
    Ignore the state, go straight.
    """
    action = {"Vm": 3}
    return action


def lqr(state):
    """ 
    Linear Quadratic Regulator
    """
    K = np.array([-2.0, 35.0, -1.5, 3.0])
    s = np.array(
        [state["theta"], state["alpha"], state["theta_dot"], state["alpha_dot"]]
    ).T
    action = {"Vm": K.dot(s)}
    return action


POLICIES = {"random": random_policy, "coast": coast, "lqr": lqr}

