"""Core package — configuration, database, logging, and exceptions."""

from app.core.config import AppSettings, get_settings
from app.core.database import AsyncSessionLocal, engine, get_db
from app.core.exceptions import (
    ConflictError,
    LeadForgeError,
    NotFoundError,
    ValidationError,
    bad_request,
    conflict,
    internal_error,
    not_found,
)
from app.core.logger import configure_logging, get_logger

__all__ = [
    # Config
    "AppSettings",
    "get_settings",
    # Database
    "engine",
    "AsyncSessionLocal",
    "get_db",
    # Exceptions
    "LeadForgeError",
    "NotFoundError",
    "ConflictError",
    "ValidationError",
    "not_found",
    "conflict",
    "bad_request",
    "internal_error",
    # Logging
    "configure_logging",
    "get_logger",
]
