"""Tests for the WebSocketClient module."""

import pytest
from pykiwoomapi import WebSocketClient


class TestWebSocketClient:
    def test_client_initialization(self, mock_auth):
        ws = WebSocketClient(mock_auth)
        assert ws.connected is False
        assert ws.is_login is False
        assert ws.keep_running is True
        assert len(ws.message_handlers) == 0

    def test_client_with_callback(self, mock_auth):
        def handler(msg):
            pass
        ws = WebSocketClient(mock_auth, callback=handler)
        assert len(ws.message_handlers) == 1

    def test_client_uri_mock(self, mock_auth):
        ws = WebSocketClient(mock_auth)
        assert "mockapi.kiwoom.com" in ws.uri

    def test_client_uri_prod(self, prod_auth):
        ws = WebSocketClient(prod_auth)
        assert "api.kiwoom.com" in ws.uri

    def test_add_message_handler(self, mock_auth):
        ws = WebSocketClient(mock_auth)
        async def handler(msg):
            pass
        ws.add_message_handler(handler)
        assert len(ws.message_handlers) == 1