"""
Fixed policies to test our sim integration with. These are intended to take
Brain states and return Brain actions.
"""

import random

def random_policy(state):
    """
    Ignore the state, move randomly.
    """
    action = {
        'command': random.randint(0, 1)
    }
    return action

def coast(state):
    """
    Ignore the state, go straight.
    """
    action = {
        'command': 1
    }
    return action

POLICIES = {"random": random_policy,
            "coast": coast}