"""Pytest fixtures for pykiwoomapi tests."""

import pytest
from pykiwoomapi import Auth, KiwoomClient


@pytest.fixture
def mock_auth():
    return Auth(mock=True)


@pytest.fixture
def prod_auth():
    return Auth(mock=False)


@pytest.fixture
def mock_client(mock_auth):
    return KiwoomClient(mock_auth)


@pytest.fixture
def prod_client(prod_auth):
    return KiwoomClient(prod_auth)