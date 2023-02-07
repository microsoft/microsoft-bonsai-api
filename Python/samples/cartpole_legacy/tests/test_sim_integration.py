import os
import pytest
import policies
from numbers import Number

new_config = {"pole_mass": 0.055, "pole_length": 0.4}

# Config with a heavier cart
large_config = {"pole_mass": 0.055, "pole_length": 0.4, "cart_mass": 0.6}


@pytest.fixture
def sim():
    from main import TemplateSimulatorSession

    sim = TemplateSimulatorSession(render=False)
    sim.episode_start(new_config)
    return sim


def test_connected(sim):

    assert sim is not None


def test_sim_config(sim):

    assert sim.config["pole_mass"] == 0.055
    assert sim.config["pole_length"] == 0.4


def test_random_action(sim):

    sim_state = sim.get_state()
    assert sim_state is not None

    random_action = policies.random_policy(sim_state)
    assert random_action is not None

    sim.episode_step(random_action)

    next_sim_state = sim.get_state()
    assert next_sim_state is not None


def test_physics(sim):
    """
    Same force should change velocity of heavier cartpole less
    """
    sim_state = sim.get_state()
    random_action = policies.random_policy(sim_state)

    sim.episode_step(random_action)
    next_state = sim.get_state()
    print(f"sim_state: {sim_state}; next_state: {next_state}")
    default_delta_v = next_state["cart_velocity"] - sim_state["cart_velocity"]

    sim.episode_start(large_config)
    sim_state = sim.get_state()
    # use the same action as above
    sim.episode_step(random_action)
    next_state = sim.get_state()
    print(f"sim_state: {sim_state}; next_state: {next_state}")

    smaller_delta_v = next_state["cart_velocity"] - sim_state["cart_velocity"]

    assert abs(smaller_delta_v) < abs(default_delta_v)


def test_sim_states(sim):

    sim_state = sim.get_state()
    assert type(sim_state) == dict
    assert len(sim_state) == 11

    for k, v in sim_state.items():
        assert isinstance(v, Number)


def test_logging():

    from main import (
        TemplateSimulatorSession,
        default_config,
    )

    sim = TemplateSimulatorSession(render=False, log_data=True, log_file_name="tmp.csv")
    for episode in range(2):
        iteration = 0
        terminal = False
        sim_state = sim.episode_start(config=default_config)
        while not terminal:
            action = policies.random_policy(sim_state)
            sim.episode_step(action)
            sim_state = sim.get_state()
            print(f"Running iteration #{iteration} for episode #{episode}")
            print(f"Observations: {sim_state}")
            sim.log_iterations(sim_state, action, episode, iteration)
            iteration += 1
            terminal = iteration >= 10
    assert sim.render == False
    assert os.path.exists(sim.log_full_path)
    os.remove("logs/tmp.csv")


def test_direction(sim, render: bool = False):
    """Test sim direction when applying constant right force"""

    sim_state = sim.get_state()
    num_steps = 100
    move_right = {"command": 1}

    for _ in range(num_steps):
        sim.episode_step(move_right)
        if render:
            sim.sim_render()

    new_state = sim.get_state()

    assert sim_state["cart_position"] <= new_state["cart_position"]

