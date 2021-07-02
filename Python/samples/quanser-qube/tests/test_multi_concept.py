"""
Pytest for confirming multi concept brain functions with learned selector,
one learned concept, and one programmed concept. Assessment with multi-concept 
is not available, so an exported brain is used. Usage:

Train a multi-concept quanser qube brain following instructions, export
to device, then run

docker run -d -p <PORT>:5000 <BRAIN_URI>

Followed by:

pytest \
    --port <PORT> \
    --render False \
    --num_iterations 640 \
    --scenario_file assess_config.json \
"""

__author__ = "Journey McDowell"
__copyright__ = "Copyright 2021, Microsoft Corp."
import os
import pytest
from functools import partial
import glob
import pandas as pd
import numpy as np

# Allowing optional flags to replace defaults for pytest from tests\conftest.py
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

# Main test function for
# 1. Run exported brain test loop for number of scenarios (1) in assess_config.json
# 2. Log exported brain data to csv
# 3. qualifying pass/fail
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