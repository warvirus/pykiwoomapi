"""Tests for the Auth module."""

import pytest
from pykiwoomapi import Auth


class TestAuth:
    def test_auth_initial_state(self, mock_auth):
        assert mock_auth.is_auth is False
        assert mock_auth.mock is True
        assert mock_auth.token is None

    def test_auth_url_mock(self, mock_auth):
        assert "mockapi.kiwoom.com" in mock_auth.url

    def test_auth_url_prod(self, prod_auth):
        assert "api.kiwoom.com" in prod_auth.url

    def test_auth_mock_flag(self, mock_auth, prod_auth):
        assert mock_auth.mock is True
        assert prod_auth.mock is False


class TestAuthMethods:
    def test_login_invalid_keys(self, mock_auth, monkeypatch):
        """Test login fails with invalid credentials."""
        class MockResponse:
            status_code = 200
            def json(self):
                return {"token": None}

        monkeypatch.setattr("requests.post", lambda *a, **k: MockResponse())
        result = mock_auth.login("invalid_key", "invalid_secret")
        assert result is False

    def test_logout_when_not_authenticated(self, mock_auth):
        result = mock_auth.logout()
        assert result is True