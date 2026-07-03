"""Add password_hash column to curators

Revision ID: 006
Revises: 005
Create Date: 2026-06-24
"""

from alembic import op  # type: ignore[attr-defined]
import sqlalchemy as sa
from _alembic_helpers import column_exists


revision: str = "006"
down_revision: str | None = "005"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    if column_exists("curators", "password_hash"):
        return
    op.add_column(
        "curators",
        sa.Column("password_hash", sa.String(255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("curators", "password_hash")
