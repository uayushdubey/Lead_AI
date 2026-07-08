"""Abstract SQLAlchemy base model for all ORM entities.

Every business model in this project inherits from ``BaseModel``::

    from app.models.base import BaseModel

    class Lead(BaseModel):
        __tablename__ = "leads"

        name: Mapped[str] = mapped_column(String(255), nullable=False)

The subclass automatically receives:
- ``id``         — UUID primary key, generated in Python before any DB call
- ``created_at`` — timezone-aware timestamp set by the DB at INSERT
- ``updated_at`` — timezone-aware timestamp set by the DB at INSERT and
                   refreshed by the DB on every UPDATE
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase):
    """Abstract base class for all SQLAlchemy ORM models.

    Design notes
    ------------
    ``__abstract__ = True``
        Tells SQLAlchemy not to create a table for this class itself.
        Each concrete subclass gets its own table via ``__tablename__``.

    UUID primary key (Python-side default)
        ``default=uuid.uuid4`` generates the UUID in Python *before* the
        INSERT statement is executed.  The ``id`` is therefore available
        on the object immediately after instantiation — no DB round-trip
        required.  This makes the object usable in unit tests and in-
        memory operations without a live database connection.

    Timezone-aware timestamps (server-side)
        Both columns use ``TIMESTAMP WITH TIME ZONE`` (``timezone=True``).
        ``server_default=func.now()`` and ``onupdate=func.now()`` delegate
        time generation to PostgreSQL so that the value is always correct
        regardless of the application server's local timezone.

    ``init=False``
        Excludes ``id``, ``created_at``, and ``updated_at`` from the
        generated ``__init__`` signature.  Callers only pass domain-
        specific columns when constructing a model instance.
    """

    __abstract__ = True

    # ── Primary key ───────────────────────────────────────────────────────────

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,   # Python-side: available before DB INSERT
        init=False,           # Excluded from __init__; auto-populated
    )

    # ── Audit timestamps ──────────────────────────────────────────────────────

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # Set by Postgres at INSERT; never changed
        nullable=False,
        init=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # Set by Postgres at INSERT
        onupdate=func.now(),        # Refreshed by Postgres on every UPDATE
        nullable=False,
        init=False,
    )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        """Return a human-readable representation for debugging.

        Example output: ``<Lead id=3fa85f64-5717-4562-b3fc-2c963f66afa6>``
        """
        pk = getattr(self, "id", None)
        return f"<{self.__class__.__name__} id={pk}>"
