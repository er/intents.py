class IntentsError(Exception):
    """Base exception for all Intents API errors."""


class IntentsAPIError(IntentsError):
    """Raised when the API returns an error response."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"HTTP {status_code}: {message}")


class IntentsAuthError(IntentsAPIError):
    """Raised when the API returns a 401 Unauthorized response."""
