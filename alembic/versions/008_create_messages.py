"""Create messages table

Revision ID: 008
Revises: None
Create Date: 2026-07-03
"""

from alembic import op  # type: ignore[attr-defined]
import sqlalchemy as sa
from _alembic_helpers import table_exists


revision: str = "008"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    if table_exists("messages"):
        return

    op.create_table(
        "messages",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("channel", sa.String(50), nullable=False),
        sa.Column("recipient", sa.String(255), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("subject", sa.String(500), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_messages_channel", "messages", ["channel"])


def downgrade() -> None:
    op.drop_index("ix_messages_channel", table_name="messages")
    op.drop_table("messages")
