"""
Tests for BonsaiClient class
Copyright 2020 Microsoft
"""

from microsoft_bonsai_api.client import Config, BonsaiClient


def test_default_client_construction():
    config = Config()
    BonsaiClient(config)
