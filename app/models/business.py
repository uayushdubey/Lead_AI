"""Business ORM model.

Represents a discovered business entity — the core record of the
LeadForge AI platform.  Every other feature (lead scoring, outreach,
opportunity analysis) relates back to a ``Business``.

Table: ``businesses``
"""

from decimal import Decimal

from sqlalchemy import Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Business(BaseModel):
    """A business discovered and tracked by LeadForge AI.

    Columns
    -------
    name : str
        Trading name of the business.  Required — a nameless record
        cannot be searched, displayed, or deduplicated.
        VARCHAR(255) / NOT NULL.

    category : str | None
        Industry or business type (e.g. "Restaurant", "Plumber").
        VARCHAR(100) / nullable.

    city : str | None
        City where the business operates.
        VARCHAR(100) / nullable.

    website : str | None
        Primary website URL.  VARCHAR(500) to accommodate long URLs;
        nullable because many small businesses have no website
        (which is itself a lead signal).

    phone : str | None
        Contact phone number.  Stored as a string (not integer) to
        preserve formatting, leading zeros, and international prefixes.
        VARCHAR(20) covers E.164 max (15 digits + separators).

    email : str | None
        Primary contact email address.
        VARCHAR(254) — RFC 5321 SMTP maximum.

    rating : Decimal | None
        Aggregate customer rating (e.g. from Google Maps or Yelp).
        ``Numeric(3, 2)`` stores exact decimal values (e.g. 4.70) with
        no IEEE 754 rounding errors — unlike ``Float``.
        Range supported: 0.00 – 9.99.  Nullable — not all sources
        provide ratings.

    Indexes
    -------
    ``ix_businesses_name``     B-tree on ``name``     (search / sort)
    ``ix_businesses_category`` B-tree on ``category`` (filter by type)
    ``ix_businesses_city``     B-tree on ``city``     (filter by location)

    Inherited from BaseModel
    ------------------------
    id         : uuid.UUID  — UUID v4, generated in Python before INSERT
    created_at : datetime   — TIMESTAMPTZ, set by DB at INSERT
    updated_at : datetime   — TIMESTAMPTZ, refreshed by DB on every UPDATE
    """

    __tablename__ = "businesses"

    __table_args__ = (
        # Searching and sorting businesses by name is the most common query.
        Index("ix_businesses_name", "name", postgresql_using="btree"),
        # Filtering businesses by industry / service category.
        Index("ix_businesses_category", "category", postgresql_using="btree"),
        # Filtering businesses by city (geographic lead targeting).
        Index("ix_businesses_city", "city", postgresql_using="btree"),
    )

    # ── Required fields ───────────────────────────────────────────────────────

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Trading name of the business",
    )

    # ── Optional contact / identity fields ────────────────────────────────────

    category: Mapped[str | None] = mapped_column(
        String(100),
        comment="Industry or business type (e.g. Restaurant, Plumber)",
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        comment="City where the business operates",
    )

    website: Mapped[str | None] = mapped_column(
        String(500),
        comment="Primary website URL; nullable — no website is a lead signal",
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        comment="Contact phone in any format; VARCHAR preserves leading zeros",
    )

    email: Mapped[str | None] = mapped_column(
        String(254),
        comment="Primary contact email (RFC 5321 max = 254 chars)",
    )

    # ── Metrics ───────────────────────────────────────────────────────────────

    rating: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=3, scale=2),
        comment="Aggregate customer rating (exact decimal, e.g. 4.70)",
    )
