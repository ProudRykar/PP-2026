"""Add parent_id column to messages

Revision ID: 003
Revises: 002
Create Date: 2026-06-19

"""

from alembic import op  # type: ignore[attr-defined]
import sqlalchemy as sa
from _alembic_helpers import column_exists, index_exists


revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade():
    if not column_exists("messages", "parent_id"):
        op.add_column("messages", sa.Column("parent_id", sa.String(), nullable=True))
    if not index_exists("messages", "ix_messages_parent_id"):
        op.create_index("ix_messages_parent_id", "messages", ["parent_id"])


def downgrade():
    op.drop_index("ix_messages_parent_id", table_name="messages")
    op.drop_column("messages", "parent_id")
