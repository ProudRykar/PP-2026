"""Add message_type column to messages

Revision ID: 002
Revises: 001
Create Date: 2026-06-12
"""

from alembic import op  # type: ignore[attr-defined]
import sqlalchemy as sa


revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "messages",
        sa.Column("message_type", sa.String(20), nullable=False, server_default="text"),
    )


def downgrade() -> None:
    op.drop_column("messages", "message_type")
