"""
Test fixtures
Copyright 2020 Microsoft
"""

import time
from multiprocessing import Process

import pytest
from _pytest.fixtures import FixtureRequest

from .web_server import start_app


@pytest.fixture(scope="session", autouse=True)
def start_server_process(request: FixtureRequest):

    proc = Process(target=start_app)
    proc.daemon = True
    proc.start()
    time.sleep(2)

    def fin():
        proc.terminate()

    request.addfinalizer(fin)
