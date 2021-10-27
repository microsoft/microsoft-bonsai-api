"""
Unit tests for Moab simulator
"""
__copyright__ = "Copyright 2020, Microsoft Corp."

# Temporarily set reportIncompatibleMethodOverride to false to work
# around a short-term bug in the typeshed stub builtins file.
# This can be removed at a later time.
# pyright: strict, reportIncompatibleMethodOverride=false

import math
from typing import Any, Dict, Iterator, TypeVar, cast

from microsoft_bonsai_api.simulator.client import BonsaiClientConfig
from bonsai_common import Schema
from moab_model import DEFAULT_PLATE_RADIUS
from moab_sim import MoabSim

_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


def run_for_duration(config: Schema, duration: float) -> MoabSim:
    """
    This uses a passed in config to init the sim and then runs
    it for a fixed duration with no actions.

    We do not connect to the platform and drive the loop ourselves.
    """
    service_config = BonsaiClientConfig(workspace="moab", access_key="utah")
    sim = MoabSim(service_config)

    # run with no actions for N seconds.
    elapsed = 0.0
    sim.episode_start(config)

    # disable noise
    sim.model.plate_noise = 0
    sim.model.ball_noise = 0
    sim.model.jitter = 0

    while elapsed < duration:
        sim.episode_step({})
        elapsed += sim.model.step_time

    # return the results
    return sim


"""
These test the speed/direction initialization at episode_start
to make sure the behaviors match expectations.

We use a flat plate and a fixed time so that final `d = vt`
"""

DURATION = 1.0  # s
SPEED = DEFAULT_PLATE_RADIUS / 4  # m/s
DIST = SPEED


def close(value: float, target: float = 0.0, epsilon: float = 0.001) -> bool:
    """ returns True is value is within epsilon of target """
    if (target - epsilon) <= value <= (target + epsilon):
        return True
    return False


def test_zero_speed_direction():
    """ test that no velocity and direction results in no motion """
    config = {
        "target_x": 0.0,
        "target_y": 0.0,
        "initial_speed": 0.0,
        "initial_direction": 0.0,
    }

    sim = run_for_duration(config, DURATION)
    assert close(sim.model.ball.x) and close(sim.model.ball.y)


def test_towards():
    """ move towards [0,0] from [-DIST,0] """
    config = {
        "time_delta": 0.010,
        "target_x": 0.0,
        "target_y": 0.0,
        "initial_x": -DIST,
        "initial_speed": SPEED,
        "initial_direction": 0.0,
    }

    sim = run_for_duration(config, DURATION)
    assert close(sim.model.ball.x) and close(sim.model.ball.y)


def test_away():
    """ move away from target """
    config = {
        "time_delta": 0.010,
        "target_x": -(DIST + 0.0001),
        "initial_x": -DIST,
        "initial_speed": SPEED,
        "initial_direction": math.radians(180),
    }

    sim = run_for_duration(config, DURATION)
    assert close(sim.model.ball.x), "Ball X coord should be zero"
    assert close(sim.model.ball.y), "Ball Y coord should be zero"


def test_angle():
    """ move from center, 90 degrees rotated from target to the left """
    config = {
        "time_delta": 0.010,
        "target_x": -(DIST),
        "target_y": 0,
        "initial_x": 0,
        "initial_y": 0,
        "initial_speed": SPEED,
        "initial_direction": math.radians(90),
    }

    sim = run_for_duration(config, DURATION)
    assert close(sim.model.ball.x), "Ball X coord should be zero"
    assert close(sim.model.ball.y, -DIST), "Ball Y coord should be -{}".format(DIST)


def test_angle2():
    config = {
        "target_x": 0,
        "target_y": DIST,
        "initial_x": 0,
        "initial_y": 0,
        "initial_speed": SPEED / 10.0,
        # just to the left
        "initial_direction": math.radians(90.0),
    }

    sim = run_for_duration(config, DURATION)
    direction = sim.model.state()["estimated_direction"]
    assert direction > 0.0, "Direction should be positive"

    # just to the right
    config["initial_direction"] = math.radians(-90.0)

    sim = run_for_duration(config, DURATION)
    direction = sim.model.state()["estimated_direction"]
    assert direction < 0.0, "Direction should be negative"


class KeyProbe(Dict[_KT, _VT]):
    """
    A "dictionary" that checks to see which keys
    are queried on it.
    """

    def __init__(self):
        self.found_keys = set()

    def get(self, key: str, default: _VT) -> _VT:
        self.found_keys.add(key)
        return default


def test_interface():
    """
    This tests that the state, config and action descriptions
    has matching values used by the model.
    """
    service_config = BonsaiClientConfig(workspace="moab", access_key="utah")
    sim = MoabSim(service_config)
    model = sim.model
    iface = sim.get_interface()
    model_state = model.state()

    # state is pull from the model

    fields = cast(Dict[str, Any], iface.description)["state"]["fields"]
    state_fields = set(cast(Iterator[str], map(lambda x: x["name"], fields)))

    # interface in state
    for attr in state_fields:
        if model_state.get(attr) is None:
            assert (
                False
            ), "Unexpected variable {} found in interface State but missing from model State.".format(
                attr
            )

    # state in interface
    for attr in model_state:
        if attr not in state_fields:
            assert (
                False
            ), "Unexpected variable {} found in model State, missing from interface State.".format(
                attr
            )

    # extract config and action from interface
    fields = cast(Dict[str, Any], iface.description)["config"]["fields"]
    config_fields = set(map(lambda x: x["name"], fields))

    # collect the model config
    config_probe = KeyProbe()  # type: KeyProbe[str, Any]
    sim.episode_start(config_probe)
    model_config = config_probe.found_keys

    # interface in config
    for attr in config_fields:
        if attr not in model_config:
            assert (
                False
            ), "Unexpected variable {} found in Config interface but missing from model Config.".format(
                attr
            )

    # state in interface
    for attr in model_config:
        if attr not in config_fields:
            assert (
                False
            ), "Unexpected variable {} found in model Config, missing from Config interface.".format(
                attr
            )

    # Now do the actions
    fields = cast(Dict[str, Any], iface.description)["action"]["fields"]
    action_fields = set(cast(Iterator[str], map(lambda x: x["name"], fields)))

    # collect the model actions
    action_probe = KeyProbe()  # type: KeyProbe[str, Any]
    sim.episode_step(action_probe)
    model_action = action_probe.found_keys

    # interface in action
    for attr in action_fields:
        if attr not in model_action:
            assert (
                False
            ), "Unexpected variable {} found in Action interface but missing from model Action.".format(
                attr
            )

    # state in action
    for attr in model_action:
        if attr not in action_fields:
            assert (
                False
            ), "Unexpected variable {} found in model Action, missing from Action interface.".format(
                attr
            )

    pass


if __name__ == "__main__":
    test_interface()
    test_zero_speed_direction()

    test_towards()
    test_away()
    test_angle()
    test_angle2()
