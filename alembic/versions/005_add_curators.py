"""Add curators, assignment_history tables and curator_id to messages

Revision ID: 005
Revises: 004
Create Date: 2026-06-24
"""

from alembic import op  # type: ignore[attr-defined]
import sqlalchemy as sa
from _alembic_helpers import table_exists, column_exists, index_exists

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if not table_exists("curators"):
        op.create_table(
            "curators",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("full_name", sa.String(255), nullable=False),
            sa.Column("login", sa.String(100), nullable=False),
            sa.Column("email", sa.String(255), nullable=False),
            sa.Column("role", sa.String(20), nullable=False, server_default="agent"),
            sa.Column("status", sa.String(20), nullable=False, server_default="active"),
            sa.Column("avatar_url", sa.String(500), nullable=True),
            sa.Column(
                "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
            ),
            sa.Column("last_activity", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("login"),
        )

    if not index_exists("curators", "ix_curators_login"):
        op.create_index("ix_curators_login", "curators", ["login"])

    if not table_exists("assignment_history"):
        op.create_table(
            "assignment_history",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("message_id", sa.String(), nullable=False),
            sa.Column("from_curator_id", sa.String(), nullable=True),
            sa.Column("to_curator_id", sa.String(), nullable=True),
            sa.Column("assigned_by", sa.String(), nullable=True),
            sa.Column("reason", sa.Text(), nullable=True),
            sa.Column(
                "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
            ),
            sa.Column("metadata", sa.JSON(), nullable=True),
            sa.ForeignKeyConstraint(
                ["message_id"], ["messages.id"], ondelete="SET NULL"
            ),
            sa.ForeignKeyConstraint(
                ["from_curator_id"], ["curators.id"], ondelete="SET NULL"
            ),
            sa.ForeignKeyConstraint(
                ["to_curator_id"], ["curators.id"], ondelete="SET NULL"
            ),
            sa.ForeignKeyConstraint(
                ["assigned_by"], ["curators.id"], ondelete="SET NULL"
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    if not index_exists("assignment_history", "ix_assignment_history_message_id"):
        op.create_index(
            "ix_assignment_history_message_id", "assignment_history", ["message_id"]
        )

    if not column_exists("messages", "curator_id"):
        op.add_column(
            "messages",
            sa.Column("curator_id", sa.String(), nullable=True),
        )

    if not index_exists("messages", "ix_messages_curator_id"):
        op.create_index("ix_messages_curator_id", "messages", ["curator_id"])


def downgrade() -> None:
    op.drop_index("ix_messages_curator_id", table_name="messages")
    op.drop_column("messages", "curator_id")
    op.drop_index("ix_assignment_history_message_id", table_name="assignment_history")
    op.drop_table("assignment_history")
    op.drop_index("ix_curators_login", table_name="curators")
    op.drop_table("curators")
