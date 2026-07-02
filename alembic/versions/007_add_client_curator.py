"""Add curator_id to clients table

Revision ID: 007
Revises: 006
Create Date: 2026-06-24
"""

from alembic import op  # type: ignore[attr-defined]
import sqlalchemy as sa

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "clients",
        sa.Column("curator_id", sa.String(), nullable=True),
    )
    op.create_index("ix_clients_curator_id", "clients", ["curator_id"])


def downgrade() -> None:
    op.drop_index("ix_clients_curator_id", table_name="clients")
    op.drop_column("clients", "curator_id")
