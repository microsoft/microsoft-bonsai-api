"""
Pytest for confirming multi concept brain functions with learned selector,
one learned concept, and one programmed concept. Evaluation is accomplished
using exported brain with an optional flag for rendering. Usage:

pytest -s \
    --acr_name <ACR_NAME> \
    --brain_name <BRAIN_NAME> \
    --port <PORT> \
    --render False \
"""

__author__ = "Journey McDowell"
__copyright__ = "Copyright 2021, Microsoft Corp."
import os
import pytest
from functools import partial
import glob
import pandas as pd
import numpy as np
import json

# Allowing optional flags to replace defaults for pytest from tests\conftest.py
@pytest.fixture()
def acr_name(pytestconfig):
    return pytestconfig.getoption("acr_name")

@pytest.fixture()
def brain_name(pytestconfig):
    return pytestconfig.getoption("brain_name")

@pytest.fixture()
def brain_version(pytestconfig):
    return pytestconfig.getoption("brain_version")

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

@pytest.fixture()
def simulator_package_name(pytestconfig):
    return pytestconfig.getoption("simulator_package_name")

@pytest.fixture()
def inkling_fname(pytestconfig):
    return pytestconfig.getoption("inkling_fname")

@pytest.fixture()
def exported_brain_name(pytestconfig):
    return pytestconfig.getoption("exported_brain_name")

@pytest.fixture()
def chip_architecture(pytestconfig):
    return pytestconfig.getoption("chip_architecture")

# Login to ACR and package simulator and push
def test_package_simulator(simulator_package_name, acr_name):
    os.system('az acr login -n {}'.format(acr_name))
    os.system('az acr build -t {} --registry {} .'.format(simulator_package_name, acr_name))
    os.system('bonsai simulator package container create -n {} -u {}.azurecr.io/{} -r 1 -m 1 -p Linux --max-instance-count 500'.format(
        simulator_package_name,
        acr_name,
        simulator_package_name,

    ))

# Use CLI to create, upload inkling, train, and wait til complete
def test_train_brain(brain_name, brain_version, inkling_fname, simulator_package_name):
    os.system('bonsai brain create -n {}'.format(
        brain_name,
    ))
    os.system('bonsai brain version update-inkling -n {} --version {} -f {}'.format(
        brain_name,
        brain_version,
        inkling_fname
    ))
    concept_names = ['Swingup', 'Balance', 'SwitchControlStrategy']
    for concept in concept_names:
        os.system('bonsai brain version start-training -n {} --version {} --simulator-package-name {} -c {}'.format(
            brain_name,
            brain_version,
            simulator_package_name,
            concept
        ))
    
        # Do not continue until training is complete
        running = True
        while running:
            os.system('bonsai brain version show --name {} --version {} -o json > status.json'.format(
                brain_name,
                brain_version,
            ))
            with open('status.json') as fname:
                status = json.load(fname)
            if status['trainingState'] == 'Active':
                pass
            else:
                running = False
                print('Training complete...')
    print('All Concepts completed')

# Use CLI to export brain and run locally on specified PORT
def test_export_and_run_brain(exported_brain_name, brain_name, brain_version, chip_architecture, port):
    os.system('bonsai exportedbrain create --name {} -bn {} -bv {} -dn exported -pa {}'.format(
        exported_brain_name,
        brain_name,
        brain_version,
        chip_architecture
    ))
    # Do not continue until export is complete
    running = True
    while running:
        os.system('bonsai exportedbrain show --name {} -o json > status.json'.format(
            exported_brain_name,
        ))
        with open('status.json') as fname:
            status = json.load(fname)
        if status['status'] == 'Succeeded':
            running = False
            print('Export success!')
        else:
            print('Export in progress..')

    # Pull docker image
    os.system('az acr login -n {}'.format(status['acrPath'].split('.azurecr.io')[0])) 
    os.system('docker pull {}'.format(status['acrPath']))
    
    # Run docker image
    os.system('docker run -d -p {}:5000 {}'.format(port, status['acrPath']))


# Main test function for
# 1. Run exported brain test loop for number of scenarios (30) in assess_config.json
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