"""Test BonsaiConnector."""
import os

import pytest
from microsoft_bonsai_api.simulator.client import BonsaiConnector


class FakeSim:
    interface = {'name': 'Fake Sim', 'timeout': 10}
    steps = 0

    def reset(self, config):
        return {}

    def step(self, action):
        self.steps += 1
        return {}


os.environ['SIM_API_HOST'] = 'http://127.0.0.1:9000'
os.environ['SIM_WORKSPACE'] = 'train'
os.environ['SIM_ACCESS_KEY'] = '111'


def test_connector_train():
    bonsai_conn = BonsaiConnector(FakeSim)
    bonsai_conn.event_loop()
    assert bonsai_conn.sim_model.steps == 95
