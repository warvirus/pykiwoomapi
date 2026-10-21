"""PyKiwoom API - Python wrapper for Kiwoom Open API+ (Korea Stock Market)"""

from ._version import __version__, __version_info__
from .auth import Auth
from .client import KiwoomClient
from .exceptions import (
    APIRequestError,
    AuthenticationError,
    PyKiwoomError,
    RateLimitError,
    WebSocketError,
)
from .realtime import WebSocketClient
from .transactions import APPID, Element, ElementReal, _Elements, _ElementsRealtime

__all__ = [
    "__version__",
    "__version_info__",
    "PyKiwoomError",
    "AuthenticationError",
    "APIRequestError",
    "WebSocketError",
    "RateLimitError",
    "Auth",
    "KiwoomClient",
    "WebSocketClient",
    "APPID",
    "_Elements",
    "_ElementsRealtime",
    "Element",
    "ElementReal",
]
