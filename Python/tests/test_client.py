"""
Tests for BonsaiClient class
Copyright 2020 Microsoft
"""
from unittest.mock import Mock, patch

import pytest
from microsoft_bonsai_api.client import Config, BonsaiClient
from azure.core.exceptions import HttpResponseError


def test_default_client_construction():
    config = Config()
    BonsaiClient(config)


# TODO: Test represents current behavor of library. It may not be what we want it to do
def test_unauthorized_registration():
    config = Config()
    config.server = "http://127.0.0.1:9000"
    config.workspace = "unauthorized"
    config.access_key = "111"

    client = BonsaiClient(config)

    try:
        client.create_session("a", 1, "c")
    except HttpResponseError as err:
        assert err.status_code == 401
        assert "Unauthorized" in err.message


# TODO: Test represents current behavor of library. It may not be what we want it to do
def test_forbidden_registration():
    config = Config()
    config.server = "http://127.0.0.1:9000"
    config.workspace = "forbidden"
    config.access_key = "111"

    client = BonsaiClient(config)

    try:
        client.create_session("a", 1, "c")
    except HttpResponseError as err:
        assert err.status_code == 403
        assert "Forbidden" in err.message


# TODO: Test represents current behavor of library. It may not be what we want it to do
def test_badgateway_registration():
    config = Config()
    config.server = "http://127.0.0.1:9000"
    config.workspace = "badgateway"
    config.access_key = "111"

    client = BonsaiClient(config)

    try:
        client.create_session("a", 1, "c")
    except HttpResponseError as err:
        assert err.status_code == 502
        assert "Bad Gateway" in err.message


# TODO: Test represents current behavor of library. It may not be what we want it to do
def test_unavailable_registration():
    config = Config()
    config.server = "http://127.0.0.1:9000"
    config.workspace = "unavailable"
    config.access_key = "111"

    client = BonsaiClient(config)

    try:
        client.create_session("a", 1, "c")
    except HttpResponseError as err:
        assert err.status_code == 503
        assert "Unavailable" in err.message


# TODO: Test represents current behavor of library. It may not be what we want it to do
def test_gateway_timeout():
    config = Config()
    config.server = "http://127.0.0.1:9000"
    config.workspace = "gatewaytimeout"
    config.access_key = "111"

    client = BonsaiClient(config)

    try:
        client.create_session("a", 1, "c")
    except HttpResponseError as err:
        assert err.status_code == 504
        assert "Gateway Timeout" in err.message


# TODO: Test represents current behavor of library. It may not be what we want it to do
def test_training():
    config = Config()
    config.server = "http://127.0.0.1:9000"
    config.workspace = "train"
    config.access_key = "111"

    client = BonsaiClient(config)
    client.create_session("a", 1, "c")

    counter = 0
    while counter < 100:
        client.advance("1", 1, {})
        counter += 1


@patch("time.sleep", return_value=None)
def test_flaky_sim(patched_sleep: Mock):
    config = Config()
    config.server = "http://127.0.0.1:9000"
    config.workspace = "flaky"
    config.access_key = "111"

    client = BonsaiClient(config)
    client.create_session("a", 1, "c")

    counter = 0
    while counter < 100:
        client.advance("1", 1, {})
        counter += 1
