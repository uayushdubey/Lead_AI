"""ORM models package.

Import BaseModel here so that Alembic's env.py picks up the full metadata
when it does ``import app.models``.  As concrete models are added, import
them in this file too::

    from app.models.lead import Lead  # noqa: F401
"""

from app.models.base import BaseModel

__all__ = ["BaseModel"]
