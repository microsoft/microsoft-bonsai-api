"""
Tests for BonsaiClient class
Copyright 2020 Microsoft
"""
from unittest.mock import Mock, patch

import pytest
from azure.core.exceptions import HttpResponseError

from microsoft_bonsai_api.simulator.client import (BonsaiClient,
                                                   BonsaiClientConfig)
from microsoft_bonsai_api.simulator.generated.models import (
    SimulatorInterface, SimulatorState)


def test_default_client_construction():
    config = BonsaiClientConfig()
    config.access_key = "1"
    config.workspace = "2"
    BonsaiClient(config)


def test_no_access_key_throws_error():
    config = BonsaiClientConfig()
    config.workspace = "1"

    with pytest.raises(RuntimeError):
        BonsaiClient(config)


def test_no_workspace_throws_error():
    config = BonsaiClientConfig()
    config.access_key = "1"
    with pytest.raises(RuntimeError):
        BonsaiClient(config)


def test_400_err_registration():
    config = BonsaiClientConfig()
    config.server = "http://127.0.0.1:9000"
    config.workspace = "badrequest"
    config.access_key = "111"

    client = BonsaiClient(config)

    try:
        interface = SimulatorInterface(name="a", timeout=1)
        client.session.create(config.workspace, interface)
    except HttpResponseError as err:
        assert err.status_code == 400


def test_401_err_registration():
    config = BonsaiClientConfig()
    config.server = "http://127.0.0.1:9000"
    config.workspace = "unauthorized"
    config.access_key = "111"

    client = BonsaiClient(config)

    try:
        interface = SimulatorInterface(name="a", timeout=1)
        client.session.create(config.workspace, interface)
    except HttpResponseError as err:
        assert err.status_code == 401


def test_403_err_registration():
    config = BonsaiClientConfig()
    config.server = "http://127.0.0.1:9000"
    config.workspace = "forbidden"
    config.access_key = "111"

    client = BonsaiClient(config)

    try:
        interface = SimulatorInterface(name="a", timeout=1)
        client.session.create(config.workspace, interface)
    except HttpResponseError as err:
        assert err.status_code == 403


def test_404_err_registration():
    config = BonsaiClientConfig()
    config.server = "http://127.0.0.1:9000"
    config.workspace = "notfound"
    config.access_key = "111"

    client = BonsaiClient(config)

    try:
        interface = SimulatorInterface(name="a", timeout=1)
        client.session.create(config.workspace, interface)
    except HttpResponseError as err:
        assert err.status_code == 404


def test_502_err_registration():
    config = BonsaiClientConfig()
    config.server = "http://127.0.0.1:9000"
    config.workspace = "badgateway"
    config.access_key = "111"

    client = BonsaiClient(config)

    try:
        interface = SimulatorInterface(name="a", timeout=1)
        client.session.create(config.workspace, interface)
    except HttpResponseError as err:
        assert err.status_code == 502


def test_503_err_registration():
    config = BonsaiClientConfig()
    config.server = "http://127.0.0.1:9000"
    config.workspace = "unavailable"
    config.access_key = "111"

    client = BonsaiClient(config)

    try:
        interface = SimulatorInterface(name="a", timeout=1)
        client.session.create(config.workspace, interface)
    except HttpResponseError as err:
        assert err.status_code == 503


def test_504_err_timeout():
    config = BonsaiClientConfig()
    config.server = "http://127.0.0.1:9000"
    config.workspace = "gatewaytimeout"
    config.access_key = "111"

    client = BonsaiClient(config)

    try:
        interface = SimulatorInterface(name="a", timeout=1)
        client.session.create(config.workspace, interface)
    except HttpResponseError as err:
        assert err.status_code == 504


def test_training():
    config = BonsaiClientConfig()
    config.server = "http://127.0.0.1:9000"
    config.workspace = "train"
    config.access_key = "111"

    client = BonsaiClient(config)

    interface = SimulatorInterface(name="a", timeout=1)
    client.session.create(config.workspace, interface)

    counter = 0
    while counter < 100:
        sim_state = SimulatorState(session_id=1, sequence_id=1, state={}, halted=False)
        client.session.advance(config.workspace, 1, body=sim_state)
        counter += 1


@patch("time.sleep", return_value=None)
def test_flaky_sim(patched_sleep: Mock):
    config = BonsaiClientConfig()
    config.server = "http://127.0.0.1:9000"
    config.workspace = "flaky"
    config.access_key = "111"

    client = BonsaiClient(config)

    interface = SimulatorInterface(name="a", timeout=1)
    client.session.create(config.workspace, interface)

    counter = 0
    while counter < 100:
        sim_state = SimulatorState(session_id=1, sequence_id=1, state={}, halted=False)
        client.session.advance(config.workspace, 1, body=sim_state)
        counter += 1
