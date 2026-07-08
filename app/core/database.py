"""Async database engine, session factory, and FastAPI session dependency.

Usage (FastAPI route):

    from app.core.database import get_db
    from sqlalchemy.ext.asyncio import AsyncSession

    @router.get("/items")
    async def list_items(db: AsyncSession = Depends(get_db)) -> list[Item]:
        ...
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import AppSettings, get_settings


def _build_engine(settings: AppSettings) -> AsyncEngine:
    """Construct the async SQLAlchemy engine from application settings.

    Design choices:
    - pool_pre_ping=True  : Silently recycles broken connections (essential in
                            Docker / cloud where the DB may restart).
    - pool_size=5         : Baseline connections kept open.  Kept conservative
                            so multiple service replicas don't exhaust Postgres
                            max_connections (default 100).
    - max_overflow=10     : Burst capacity; total peak = 5 + 10 = 15 per replica.
    - echo=debug          : Prints SQL only when APP_DEBUG=true — never in prod.
    - pool_timeout=30     : Wait up to 30 s for a connection before raising.
    """
    return create_async_engine(
        str(settings.database_url),
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        echo=settings.app_debug,
    )


def _build_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create the async sessionmaker bound to the given engine.

    Design choices:
    - expire_on_commit=False : After commit, ORM attributes stay accessible
                               without issuing a second SELECT.  Without this,
                               accessing a field on a returned model after commit
                               raises MissingGreenlet in async context.
    - autoflush=False        : Explicit control — we flush when we choose to,
                               preventing surprise SQL in read-only paths.
    - autobegin=True (default): Each session starts a transaction lazily on
                               first DB operation; we commit/rollback explicitly.
    """
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


# ── Module-level singletons ───────────────────────────────────────────────────
# Built once at import time.  Tests can rebuild by calling the factory
# functions with a test-specific engine.

_settings: AppSettings = get_settings()
engine: AsyncEngine = _build_engine(_settings)
AsyncSessionLocal: async_sessionmaker[AsyncSession] = _build_session_factory(engine)


# ── FastAPI dependency ────────────────────────────────────────────────────────

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session scoped to a single HTTP request.

    Session lifecycle:
    - A new session is opened at the start of every request.
    - On success   → the session is committed, then closed.
    - On exception → the session is rolled back, then closed; the
                     exception propagates so FastAPI can return the
                     appropriate HTTP error response.

    The `async with` block guarantees the session is always closed, even
    if rollback itself raises (highly unlikely but handled by the context
    manager internals).
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
