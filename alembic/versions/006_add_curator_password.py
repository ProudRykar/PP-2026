"""Add password_hash column to curators

Revision ID: 006
Revises: 005
Create Date: 2026-06-24
"""

from alembic import op  # type: ignore[attr-defined]
import sqlalchemy as sa

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "curators",
        sa.Column("password_hash", sa.String(255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("curators", "password_hash")
