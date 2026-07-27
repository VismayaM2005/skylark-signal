class MondayAPIError(Exception):
    """Base exception for all monday.com integration errors."""
    pass

class MondayAuthError(MondayAPIError):
    """Raised when authentication fails (401 Unauthorized / Invalid token)."""
    pass

class MondayPermissionError(MondayAPIError):
    """Raised when access is forbidden (403 Forbidden)."""
    pass

class MondayBoardNotFoundError(MondayAPIError):
    """Raised when a requested board ID cannot be found on monday.com."""
    pass

class MondayRateLimitError(MondayAPIError):
    """Raised when API rate limits or complexity limits are exceeded (429 / ComplexityException)."""
    pass

class MondayEmptyBoardError(MondayAPIError):
    """Raised when a board exists but contains 0 items."""
    pass

class MondaySchemaMismatchError(MondayAPIError):
    """Raised when required canonical fields cannot be mapped from board columns."""
    pass

class MondayTimeoutError(MondayAPIError):
    """Raised when request to monday.com times out."""
    pass

class MondayMalformedResponseError(MondayAPIError):
    """Raised when response JSON is malformed or missing expected data keys."""
    pass
