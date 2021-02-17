import os
import pytest
import policies

new_config = {"masspole": 0.5, "length": 0.9, "noise": 0.05}
large_config = {"masspole": 1.5, "length": 0.9, "noise": 0.05}


@pytest.fixture
def sim():
    from main import (
        TemplateSimulatorSession,
        default_config,
    )

    sim = TemplateSimulatorSession(render=False)
    sim.episode_start(new_config)
    return sim


def test_connected(sim):

    assert sim is not None


def test_sim_config(sim):

    assert sim.config["masspole"] == 0.5
    assert sim.config["length"] == 0.9
    assert sim.config["noise"] == 0.05


def test_random_action(sim):

    sim_state = sim.get_state()
    assert sim_state is not None

    random_action = policies.random_policy(sim_state)
    assert random_action is not None

    sim.episode_step(random_action)

    next_sim_state = sim.get_state()
    assert next_sim_state is not None


def test_pole_displacement(sim):

    sim_state = sim.get_state()
    random_action = policies.random_policy(sim_state)

    sim.episode_step(random_action)
    next_state = sim.get_state()

    default_displacement = next_state["x_position"] - sim_state["x_position"]

    sim.episode_start(large_config)
    sim_state = sim.get_state()
    random_action = policies.random_policy(sim_state)

    sim.episode_step(random_action)
    next_state = sim.get_state()

    smaller_displacement = next_state["x_position"] - sim_state["x_position"]

    assert abs(smaller_displacement) < abs(default_displacement)


def test_sim_states(sim):

    sim_state = sim.get_state()
    assert type(sim_state) == dict
    assert len(sim_state) == 4

    for k, v in sim_state.items():
        assert type(v) == float


def test_logging():

    from main import (
        TemplateSimulatorSession,
        default_config,
    )

    sim = TemplateSimulatorSession(render=False, log_data=True, log_file="tmp.csv")
    for episode in range(2):
        iteration = 0
        terminal = False
        sim_state = sim.episode_start(config=default_config)
        while not terminal:
            action = sim.random_policy(sim_state)
            sim.episode_step(action)
            sim_state = sim.get_state()
            print(f"Running iteration #{iteration} for episode #{episode}")
            print(f"Observations: {sim_state}")
            sim.log_iterations(sim_state, action, episode, iteration)
            iteration += 1
            terminal = iteration >= 10
    assert sim.render == False
    assert os.path.exists(sim.log_file)
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

    assert sim_state["x_position"] <= new_state["x_position"]

