"""Alembic migration environment — SQLAlchemy 2.0 async, PostgreSQL.

This file is executed by Alembic for every ``alembic`` CLI command.

Two execution modes
-------------------
Offline mode  (``alembic upgrade head --sql``)
    Renders migration SQL to stdout without connecting to the database.
    Useful for review or when a DBA applies changes manually.

Online mode   (``alembic upgrade head``)
    Connects to the database and applies migrations directly.
    Uses the application's async engine so no second engine is created.

Adding a new model
------------------
1. Create the model in ``app/models/<name>.py``.
2. Import it in ``app/models/__init__.py``.
3. Run ``alembic revision --autogenerate -m "describe_the_change"``.
4. Review the generated file in ``alembic/versions/``.
5. Run ``alembic upgrade head``.
"""

import asyncio
import logging
from logging.config import fileConfig
from typing import Any

from alembic import context
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

# ── Application imports ───────────────────────────────────────────────────────

from app.core.config import get_settings
from app.core.database import engine  # reuse the application engine
from app.models.base import BaseModel

# Register all concrete models so Alembic sees their tables.
# Every new model file MUST be imported in app/models/__init__.py.
import app.models  # noqa: F401

# ── Alembic configuration ─────────────────────────────────────────────────────

alembic_config = context.config
settings = get_settings()

# Wire stdlib logging from alembic.ini (only if a config file is present)
if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

logger = logging.getLogger("alembic.env")

# The metadata object that drives autogenerate comparisons.
# BaseModel.metadata accumulates table definitions from all imported models.
target_metadata = BaseModel.metadata


# ── Helper ────────────────────────────────────────────────────────────────────

def _get_context_kwargs() -> dict[str, Any]:
    """Return the shared kwargs for context.configure().

    Centralised here so offline and online mode use identical settings.

    compare_type=True
        Detect column type changes (e.g. String(100) → String(255)).
        Without this, type changes are silently ignored during autogenerate.

    compare_server_default=True
        Detect changes to server_default values.
        Without this, server_default drift is invisible to autogenerate.

    include_schemas=False
        We use the default Postgres search_path (public).  Set to True if
        the project ever adds multi-schema support.
    """
    return {
        "target_metadata": target_metadata,
        "compare_type": True,
        "compare_server_default": True,
        "include_schemas": False,
        # Render NULL / NOT NULL explicitly in generated SQL
        "render_item": None,
    }


# ── Offline mode ──────────────────────────────────────────────────────────────

def run_migrations_offline() -> None:
    """Render migration SQL to stdout without a live DB connection.

    Useful for:
    - Reviewing SQL before applying to production.
    - Environments where direct DB access is restricted.

    Run with:  alembic upgrade head --sql
    """
    url = str(settings.database_url)
    logger.info("Running offline migrations against: %s", url)

    context.configure(
        url=url,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **_get_context_kwargs(),
    )

    with context.begin_transaction():
        context.run_migrations()


# ── Online mode ───────────────────────────────────────────────────────────────

def _run_migrations_on_connection(connection: Connection) -> None:
    """Execute migrations on an already-open synchronous connection.

    This is called via ``connection.run_sync(...)`` which bridges the async
    engine to Alembic's synchronous migration runner.
    """
    context.configure(connection=connection, **_get_context_kwargs())

    with context.begin_transaction():
        context.run_migrations()


async def _run_migrations_async(async_engine: AsyncEngine) -> None:
    """Open an async connection and delegate to the sync migration runner."""
    async with async_engine.connect() as connection:
        await connection.run_sync(_run_migrations_on_connection)


def run_migrations_online() -> None:
    """Apply migrations against a live database using the application engine.

    We reuse ``app.core.database.engine`` rather than creating a second
    engine so that pool configuration is never duplicated.
    """
    logger.info("Running online migrations")
    asyncio.run(_run_migrations_async(engine))


# ── Entry point ───────────────────────────────────────────────────────────────

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
