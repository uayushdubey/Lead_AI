"""Domain and HTTP exception hierarchy."""

from fastapi import HTTPException, status


class LeadForgeError(Exception):
    """Base class for all application errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(LeadForgeError):
    """Raised when a requested resource does not exist."""


class ConflictError(LeadForgeError):
    """Raised when an operation conflicts with existing state."""


class ValidationError(LeadForgeError):
    """Raised when input data fails business-rule validation."""


# ── HTTP helpers ──────────────────────────────────────────────────────────────

def not_found(detail: str = "Resource not found") -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def conflict(detail: str = "Resource already exists") -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


def bad_request(detail: str = "Bad request") -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def internal_error(detail: str = "Internal server error") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
    )
