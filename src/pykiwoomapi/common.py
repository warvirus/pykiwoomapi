"""Common utilities and HTTP client for PyKiwoom API."""

import logging
from abc import abstractmethod
from typing import Any, Dict, Optional

import requests
from requests.exceptions import ConnectionError as ReqConnectionError
from requests.exceptions import HTTPError, RequestException, Timeout

from ._version import __version__


def host_url(mock: bool) -> str:
    """Get the API base URL.

    Args:
        mock: If True, returns mock environment URL.

    Returns:
        API base URL string.
    """
    return "https://mockapi.kiwoom.com" if mock else "https://api.kiwoom.com"


class WebIo:
    """Base HTTP client for Kiwoom API requests."""

    def __init__(self) -> None:
        self.headers: Dict[str, str] = {
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": f"pykiwoomapi/{__version__}",
        }

    @property
    @abstractmethod
    def url(self) -> str:
        raise NotImplementedError

    def read(self, **params: Any) -> requests.Response:
        """Send a POST request.

        Args:
            **params: URL parameters including 'url', 'json', 'data'.

        Returns:
            Response object.
        """
        url = params.get("url", self.url)
        json_data = params.get("json")
        data = params.get("data")

        resp = requests.post(url, headers=self.headers, data=data, json=json_data)
        if resp.status_code == 200:
            logging.debug("Status: %s", resp.status_code)
        else:
            logging.error("Status: %s", resp.status_code)

        return resp


def api_request(
    mock: bool,
    token: Optional[str],
    api_id: str,
    urn: str,
    cont_yn: str = "N",
    next_key: str = "",
    timeout: int = 30,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Send a request to the Kiwoom API.

    Args:
        mock: Use mock environment.
        token: Bearer token for authentication.
        api_id: API identifier.
        urn: URL path segment.
        cont_yn: Continuation flag ('Y' or 'N').
        next_key: Pagination key for subsequent requests.
        timeout: Request timeout in seconds.
        **kwargs: Request body data.

    Returns:
        API response dictionary.
    """
    if not token:
        return {"return_code": -1, "return_msg": "No token provided. Please authenticate first."}

    url = f"{host_url(mock)}/api/dostk/{urn}"

    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "authorization": f"Bearer {token}",
        "cont-yn": cont_yn,
        "next-key": next_key,
        "api-id": api_id,
    }

    data = kwargs.get("data", kwargs)

    ret: Dict[str, Any] = {"return_code": -1, "return_msg": ""}

    try:
        resp = requests.post(url, headers=headers, json=data, timeout=timeout)
        if resp.status_code == 200:
            logging.debug("Status: %s", resp.status_code)
            logging.debug("Body: %s", resp.json())
            ret = resp.json()
        else:
            if resp.status_code != 429:
                logging.error("Status: %s", resp.status_code)
            ret["return_code"] = resp.status_code

    except HTTPError as e:
        ret["return_msg"] = f"HTTP error: {e}"
        logging.error(ret["return_msg"])
    except Timeout:
        ret["return_msg"] = "Request timed out."
        logging.error(ret["return_msg"])
    except ReqConnectionError:
        ret["return_msg"] = "Connection error."
        logging.error(ret["return_msg"])
    except RequestException as e:
        ret["return_msg"] = f"Request error: {e}"
        logging.error(ret["return_msg"])
    except Exception as e:
        ret["return_msg"] = f"Unexpected error: {e}"
        logging.error(ret["return_msg"])

    return ret