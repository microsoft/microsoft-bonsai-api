"""
Unit tests for Moab physics model
"""
__copyright__ = "Copyright 2020, Microsoft Corp."

# pyright: strict

import time
import os

from bonsai_common import Schema
from microsoft_bonsai_api.simulator.client import BonsaiClientConfig
from moab_model import MoabModel
from moab_sim import MoabSim


def run_model_for_count(count: int):
    """ Runs the model without actions for a duration """
    # sync the plate position with commanded position
    model = MoabModel()
    model.reset()
    model.update_plate(True)

    model.plate_noise = 0
    model.ball_noise = 0
    model.jitter = 0

    # run for count
    iterations = 0
    while iterations < count:
        model.step()
        iterations += 1


def run_sim_for_count(config: Schema, action: Schema, count: int) -> MoabSim:
    """
    This uses a passed in config to init the sim and then runs
    it for a fixed duration with no actions.

    We do not connect to the platform and drive the loop ourselves.
    """
    service_config = BonsaiClientConfig(workspace="moab", access_key="utah")
    sim = MoabSim(service_config)

    # run with no actions for N seconds.
    sim.episode_start(config)

    # disable noise
    sim.model.plate_noise = 0
    sim.model.ball_noise = 0
    sim.model.jitter = 0

    iterations = 0
    while iterations < count:
        sim.episode_step(action)
        iterations += 1

    # return the results
    return sim


"""
Speed tests.

Run the simulation for N runs, M times each.
Average FPS count and assert if it drops below threshold.

This tests for:
- regressions in simulator performance
"""

# constants for speed tests
MAX_RUNS = 10
MAX_ITER = 250

# use FPS fail limit from env if it is available
ENV_FPS_FAIL_LIMIT = os.environ.get("MOAB_PERF_TEST_THRESHOLD")
FPS_FAIL_LIMIT = int(ENV_FPS_FAIL_LIMIT) if ENV_FPS_FAIL_LIMIT else 500


def test_model_perf():
    avg_fps = 0
    for _ in range(0, MAX_RUNS):

        start = time.time()
        run_model_for_count(MAX_ITER)
        end = time.time()

        fps = MAX_ITER / (end - start)
        avg_fps = avg_fps + fps
    avg_fps /= MAX_RUNS

    print("model average avg fps: ", avg_fps)
    assert (
        avg_fps > FPS_FAIL_LIMIT
    ), "Iteration speed for Model dropped below {} fps.".format(FPS_FAIL_LIMIT)


def test_sim_perf():
    avg_fps = 0
    for _ in range(0, MAX_RUNS):
        start = time.time()
        run_sim_for_count(
            {},
            {
                "input_pitch": 0.0,
                "input_roll": 0.0,
            },
            MAX_ITER,
        )
        end = time.time()

        fps = MAX_ITER / (end - start)
        avg_fps = avg_fps + fps
    avg_fps /= MAX_RUNS

    print("simulator average avg fps: ", avg_fps)
    assert (
        avg_fps > FPS_FAIL_LIMIT
    ), "Iteration speed for Simulator dropped below {} fps.".format(FPS_FAIL_LIMIT)


if __name__ == "__main__":
    test_model_perf()
    test_sim_perf()
