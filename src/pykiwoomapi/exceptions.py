"""Custom exceptions for pykiwoomapi."""


class PyKiwoomError(Exception):
    """Base exception for pykiwoomapi."""
    pass


class AuthenticationError(PyKiwoomError):
    """Raised when authentication fails."""
    pass


class APIRequestError(PyKiwoomError):
    """Raised when an API request fails."""

    def __init__(self, code: int, msg: str) -> None:
        self.code = code
        self.msg = msg
        super().__init__(f"API Error [{code}]: {msg}")


class WebSocketError(PyKiwoomError):
    """Raised when a WebSocket connection or communication fails."""
    pass


class RateLimitError(PyKiwoomError):
    """Raised when the API rate limit is exceeded."""
    pass