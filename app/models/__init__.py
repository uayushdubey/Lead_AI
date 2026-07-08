"""ORM models package.

All models imported here are automatically discovered by Alembic's
``env.py`` (via ``import app.models``) during autogenerate.

When adding a new model:
1. Create ``app/models/<name>.py`` with the model class.
2. Import it below with a ``# noqa: F401`` comment.
3. Run ``alembic revision --autogenerate -m "describe_change"``.
"""

from app.models.base import BaseModel
from app.models.business import Business  # noqa: F401

__all__ = [
    "BaseModel",
    "Business",
]
