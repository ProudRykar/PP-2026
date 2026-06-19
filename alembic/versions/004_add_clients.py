"""Add clients and client_channels tables

Revision ID: 004
Revises: 003
Create Date: 2026-06-19
"""

from alembic import op  # type: ignore[attr-defined]
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False, server_default=""),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column("last_interaction", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "client_channels",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("client_id", sa.String(), nullable=False),
        sa.Column("channel", sa.String(50), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_client_channels_client_id", "client_channels", ["client_id"])
    op.create_index(
        "ix_client_channels_channel_external_id",
        "client_channels",
        ["channel", "external_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_client_channels_channel_external_id", table_name="client_channels"
    )
    op.drop_index("ix_client_channels_client_id", table_name="client_channels")
    op.drop_table("client_channels")
    op.drop_table("clients")
