"""Authentication module for PyKiwoom API."""

import logging
from typing import Any, Dict, List, Optional, Union

from .common import host_url, WebIo


class Auth(WebIo):
    """Handles OAuth2 authentication with Kiwoom API servers.

    Args:
        mock: If True, uses mock/demo environment. If False, uses production.
        appkey: Optional application key from Kiwoom API portal.
        secretkey: Optional secret key from Kiwoom API portal.
        logger: Optional external logger. If None, uses default logging.
    """

    def __init__(
        self,
        mock: bool = False,
        appkey: Optional[str] = None,
        secretkey: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        super().__init__()
        self._mock: bool = mock
        self._appkey: Optional[str] = appkey
        self._secretkey: Optional[str] = secretkey
        self._token: Optional[str] = None
        self._logger: logging.Logger = logger if logger else logging.getLogger(__name__)

    @property
    def mock(self) -> bool:
        return self._mock

    @property
    def token(self) -> Optional[str]:
        return self._token

    @property
    def is_auth(self) -> bool:
        return self._token is not None

    @property
    def url(self) -> str:
        return host_url(self._mock)

    @property
    def appkey(self) -> Optional[str]:
        return self._appkey

    @property
    def secretkey(self) -> Optional[str]:
        return self._secretkey

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @logger.setter
    def logger(self, logger: logging.Logger) -> None:
        self._logger = logger

    def login(
        self,
        appkey: Optional[str] = None,
        secretkey: Optional[str] = None,
        mock: Optional[bool] = None,
        results: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """Authenticate with Kiwoom API using app key and secret key.

        Args:
            appkey: Application key from Kiwoom API portal.
                   If None, uses stored appkey from __init__.
            secretkey: Secret key from Kiwoom API portal.
                      If None, uses stored secretkey from __init__.
            mock: Optional boolean to override the mock setting.
            results: Optional list to store login response data.

        Returns:
            True if login successful, False otherwise.
        """
        result = False

        if mock is not None:
            self._mock = mock

        if appkey is None:
            appkey = self._appkey
        if secretkey is None:
            secretkey = self._secretkey

        if results is None:
            results = []

        if not appkey or not secretkey:
            results.append({"return_code": -1, "return_msg": "appkey and secretkey are required"})
            self._logger.error("appkey and secretkey are required")
        else:
            params = {
                "grant_type": "client_credentials",
                "appkey": appkey,
                "secretkey": secretkey,
            }

            try:
                url = host_url(self._mock) + "/oauth2/token"
                res = self.read(url=url, json=params)
                if res.status_code == 200:
                    data = res.json()
                    results.append(data)

                    if "token" in data and data["token"]:
                        self._token = data["token"]
                        self._appkey = appkey
                        self._secretkey = secretkey
                        result = True
                    else:
                        error_msg = data.get("return_msg", "No token in response")
                        error_data = {"return_code": -1, "return_msg": error_msg}
                        results.append(error_data)
                        self._logger.error(f"Login failed: {error_msg}")
                else:
                    error_data = {"return_code": res.status_code, "return_msg": res.text}
                    results.append(error_data)
                    self._logger.error(f"Login failed: HTTP {res.status_code} - {res.text}")
            except Exception as e:
                error_data = {"return_code": -1, "return_msg": str(e)}
                results.append(error_data)
                self._token = None
                self._logger.error(e)

        return result

    def logout(self) -> bool:
        """Revoke the access token."""
        if self._token is None:
            return True

        params = {
            "grant_type": "client_credentials",
            "appkey": self._appkey,
            "secretkey": self._secretkey,
            "token": self._token,
        }

        try:
            url = host_url(self._mock) + "/oauth2/revoke"
            res = self.read(url=url, json=params)
            if res.status_code == 200:
                self._token = None
                return True
        except Exception:
            pass

        return False