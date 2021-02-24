"""
Fixed policies to test our sim integration with. These are intended to take
Brain states and return Brain actions.
"""

import numpy as np

def random_policy(state):
    """
    Ignore the state, move randomly.
    """
    action = {
        'input_roll': np.random.uniform(-1, 1),
        'input_pitch': np.random.uniform(-1,1)
    }
    return action

def coast(state):
    """
    Ignore the state, go straight.
    """
    action = {
        'input_roll': 0,
        'input_pitch': 0
    }
    return action

POLICIES = {"random": random_policy,
            "coast": coast}