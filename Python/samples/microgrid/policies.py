"""
Fixed policies to test our sim integration with. These are intended to take
Brain states and return Brain actions.
"""

import random
from typing import Dict
import requests


# These max levels are specific to the microgrid we are working with in the sample
max_pv_level = 73225.11
max_battery_charge_discharge = 16327
max_grid_import_export = 99625

def random_policy(state):
    """
    Ignore the state, generate actions randomly.
    """
    action = {}
    action["pv_to_consume"] = random.uniform(0, max_pv_level)
    action["battery_power"] = random.uniform(-max_battery_charge_discharge, max_battery_charge_discharge)
    action["grid_power"] = random.uniform(-max_grid_import_export, max_grid_import_export)
    return action


def rule_based(state):
    """
    Baseline, rule based policy.
    """
    action = {}
    load = state['load']
    pv = state['pv']
    capa_to_charge = state['capa_to_charge']
    capa_to_dischare = state['capa_to_discharge']
    p_disc = max(0, min(load - pv, capa_to_dischare, max_battery_charge_discharge))
    p_char = max(0, min(pv - load, capa_to_charge, max_battery_charge_discharge))

    if load - pv >=  0:

        #action['pv_to_consume'] = min(pv, load)
        action['battery_power'] = -p_disc
        #action['grid_power'] = max(0, load - pv - p_disc)

    else:
        
        #action['pv_to_consume'] = min(pv, load + p_char)
        action['battery_power'] = p_char
        #action['grid_power'] = - max(0,pv - load - p_char)
    
    return action


def brain_policy(
    state: Dict[str, float], exported_brain_url: str = "http://localhost:5000"
):

    prediction_endpoint = f"{exported_brain_url}/v1/prediction"
    response = requests.get(prediction_endpoint, json=state)
    action = response.json()
    return action
