"""Add senders and sender_identities tables

Revision ID: 001
Revises: 008
Create Date: 2026-06-04
"""

from alembic import op  # type: ignore[attr-defined]
import sqlalchemy as sa
from _alembic_helpers import table_exists, column_exists, index_exists


revision: str = "001"
down_revision: str | None = "008"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    if not table_exists("senders"):
        op.create_table(
            "senders",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column(
                "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    if not table_exists("sender_identities"):
        op.create_table(
            "sender_identities",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("sender_id", sa.String(), nullable=False),
            sa.Column("channel", sa.String(50), nullable=False),
            sa.Column("address", sa.String(255), nullable=False),
            sa.ForeignKeyConstraint(["sender_id"], ["senders.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not index_exists("sender_identities", "ix_sender_identities_sender_id"):
        op.create_index(
            "ix_sender_identities_sender_id", "sender_identities", ["sender_id"]
        )

    if not index_exists("sender_identities", "ix_sender_identities_channel_address"):
        op.create_index(
            "ix_sender_identities_channel_address",
            "sender_identities",
            ["channel", "address"],
        )

    if not column_exists("messages", "sender_id"):
        op.add_column("messages", sa.Column("sender_id", sa.String(), nullable=True))

    if not index_exists("messages", "ix_messages_sender_id"):
        op.create_index("ix_messages_sender_id", "messages", ["sender_id"])


def downgrade() -> None:
    op.drop_index("ix_messages_sender_id", table_name="messages")
    op.drop_column("messages", "sender_id")
    op.drop_index(
        "ix_sender_identities_channel_address", table_name="sender_identities"
    )
    op.drop_index("ix_sender_identities_sender_id", table_name="sender_identities")
    op.drop_table("sender_identities")
    op.drop_table("senders")
