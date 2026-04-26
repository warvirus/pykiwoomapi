"""Tests for the KiwoomClient module."""

import pytest
from pykiwoomapi import KiwoomClient, APPID


class TestKiwoomClient:
    def test_client_initial_state(self, mock_client):
        assert mock_client.is_auth is False
        assert mock_client.auth is not None

    def test_read_unknown_command(self, mock_client):
        result = mock_client.read(" nonexistent_command")
        assert result["return_code"] == -1
        assert "Unknown command" in result["return_msg"]


class TestAPPID:
    def test_appid_not_empty(self):
        assert len(APPID) > 0

    def test_appid_contains_stock_command(self):
        assert "주식기본정보요청" in APPID

    def test_appid_contains_account_commands(self):
        assert "예수금상세현황요청" in APPID

    def test_appid_structure(self):
        for cmd, value in APPID.items():
            assert isinstance(cmd, str)
            assert isinstance(value, list)
            assert len(value) == 2
            assert isinstance(value[0], str)
            assert isinstance(value[1], str)