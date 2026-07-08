"""Structured logging configuration using structlog.

Call `configure_logging(settings)` exactly once at application startup
(inside `main.py` lifespan or at module level before the app is created).

After that, any module can do:

    from app.core.logger import get_logger

    logger = get_logger(__name__)
    logger.info("user_created", user_id=str(user.id))

Adding per-request context (e.g. request_id) uses structlog contextvars:

    import structlog
    structlog.contextvars.bind_contextvars(request_id="abc-123")
    # All subsequent log calls in this coroutine automatically include it.
    structlog.contextvars.clear_contextvars()
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor

from app.core.config import AppSettings


def _build_shared_processors() -> list[Processor]:
    """Processors that run on every log record, regardless of environment.

    Order matters — each processor receives the output of the previous one.
    """
    return [
        # Inject contextvars (e.g. request_id bound per-request)
        structlog.contextvars.merge_contextvars,
        # Add "level" key  (e.g. "info", "error")
        structlog.stdlib.add_log_level,
        # Add "logger" key from the logger name passed to get_logger()
        structlog.stdlib.add_logger_name,
        # Add "timestamp" in ISO-8601 format
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        # Expand positional args: logger.info("Hello %s", name)
        structlog.stdlib.PositionalArgumentsFormatter(),
        # Render exception info attached to the log record
        structlog.processors.StackInfoRenderer(),
        # Format exc_info tuples into readable tracebacks
        structlog.processors.ExceptionRenderer(),
    ]


def _build_renderer(debug: bool) -> Processor:
    """Select the terminal renderer based on environment.

    Development  → ConsoleRenderer  (colourised, human-readable)
    Production   → JSONRenderer     (machine-parseable; Datadog / ELK friendly)
    """
    if debug:
        return structlog.dev.ConsoleRenderer(colors=True)
    return structlog.processors.JSONRenderer()


def configure_logging(settings: AppSettings) -> None:
    """Set up stdlib root logger + structlog pipeline.

    Must be called once before any log calls are made.
    Calling it multiple times is safe (idempotent).

    Args:
        settings: The application settings instance.
    """
    log_level: int = logging.DEBUG if settings.app_debug else logging.INFO

    shared_processors = _build_shared_processors()
    renderer = _build_renderer(settings.app_debug)

    # ── Configure structlog ───────────────────────────────────────────────────
    structlog.configure(
        processors=[
            *shared_processors,
            # Prepare the event dict for the stdlib ProcessorFormatter
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # ── Configure stdlib root logger via ProcessorFormatter ───────────────────
    # This ensures that third-party libraries logging via stdlib
    # (e.g. SQLAlchemy, uvicorn, httpx) also go through structlog processors.
    formatter = structlog.stdlib.ProcessorFormatter(
        # Pre-chain runs for foreign (stdlib) log records only
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Quieten noisy third-party loggers in production
    if not settings.app_debug:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str, **initial_values: Any) -> structlog.stdlib.BoundLogger:
    """Return a named structlog BoundLogger.

    Args:
        name:           Logger name (typically ``__name__``).
        **initial_values: Key-value pairs permanently bound to this logger
                          instance (e.g. ``component="auth"``).

    Returns:
        A structlog BoundLogger ready for use.

    Example::

        logger = get_logger(__name__, component="auth")
        logger.info("token_issued", user_id=str(user.id), expires_in=3600)
    """
    logger: structlog.stdlib.BoundLogger = structlog.get_logger(name)  # type: ignore[assignment]
    if initial_values:
        logger = logger.bind(**initial_values)
    return logger
