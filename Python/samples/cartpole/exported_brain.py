
import requests
from typing import Dict
from sim.simulator_model import SimulatorModel
import random

def brain_policy(state: Dict[str, float], exported_brain_url):
    
    prediction_endpoint = f"{exported_brain_url}/v1/prediction"
    response = requests.get(prediction_endpoint, json=state)

    return response.json()

def test_policy(
    render,
    exported_brain_iterations,
    exported_brain_episodes,
    exported_brain_url
):
    """Test an exported brain policy over a fixed number of episodes
    """
    sim = SimulatorModel()
    
    for episode in range(exported_brain_episodes):
        iteration = 0
        terminal = False
        # When testing, initialize throughout the range.
        config = {"initial_cart_position": random.uniform(-0.9, 0.9)}
        sim_state = sim.reset(config=config)
        while not terminal:
            action = brain_policy(sim_state, exported_brain_url=exported_brain_url)
            sim_state = sim.step(action)
            print(f"Running iteration #{iteration} for episode #{episode}")
            print(f"Action: {action}")
            print(f"State: {sim_state}")
            iteration += 1
            terminal = iteration >= exported_brain_iterations

    return sim