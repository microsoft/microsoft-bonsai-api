import os
import pytest
from functools import partial
import glob
import pandas as pd
import numpy as np

@pytest.fixture()
def port(pytestconfig):
    return pytestconfig.getoption("port")

@pytest.fixture()
def render(pytestconfig):
    return pytestconfig.getoption("render")

@pytest.fixture()
def num_iterations(pytestconfig):
    return pytestconfig.getoption("num_iterations")

@pytest.fixture()
def scenario_file(pytestconfig):
    return pytestconfig.getoption("scenario_file")

def test_exported_brain(port, render, num_iterations, scenario_file):
    from policies import brain_policy
    from main import test_policy
    url = f"http://localhost:{port}"
    print(f"Connecting to exported brain running at {url}...")
    trained_brain_policy = partial(brain_policy, exported_brain_url=url)
    test_policy(
        render=render,
        log_iterations=True,
        policy=trained_brain_policy,
        policy_name="exported",
        num_iterations=num_iterations,
        scenario_file=scenario_file,
    )

    files = glob.glob('logs/' + '/*csv')
    max_file = max(files, key=os.path.getctime)

    with open(max_file) as fname:
        df = pd.read_csv(fname)

    assert np.mean(df['state_alpha'].iloc[-400:]) <= 0.03
    assert np.mean(df['state_alpha_dot'].iloc[-400:]) <= 0.01