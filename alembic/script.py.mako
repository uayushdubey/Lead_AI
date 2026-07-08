"""${message}

Revision ID: ${up_revision}
Revises:     ${down_revision | comma,n}
Create Date: ${create_date}

Usage
-----
Apply:    alembic upgrade head
Rollback: alembic downgrade -1
SQL only: alembic upgrade head --sql
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

${imports if imports else ""}

# ── Revision metadata ─────────────────────────────────────────────────────────

revision: str = ${repr(up_revision)}
down_revision: str | None = ${repr(down_revision)}
branch_labels: str | Sequence[str] | None = ${repr(branch_labels)}
depends_on: str | Sequence[str] | None = ${repr(depends_on)}


# ── Migration ─────────────────────────────────────────────────────────────────

def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
