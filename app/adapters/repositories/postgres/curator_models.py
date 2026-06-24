from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    JSON,
    ForeignKey,
    PrimaryKeyConstraint,
)
from sqlalchemy.sql import func

from app.adapters.gateways.postgres import Base


class CuratorModel(Base):
    __tablename__ = "curators"

    id = Column(String, primary_key=True)
    full_name = Column(String(255), nullable=False)
    login = Column(String(100), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, server_default="agent")
    status = Column(String(20), nullable=False, server_default="active")
    avatar_url = Column(String(500), nullable=True)
    password_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (PrimaryKeyConstraint("id"),)


class AssignmentHistoryModel(Base):
    __tablename__ = "assignment_history"

    id = Column(String, primary_key=True)
    message_id = Column(
        String,
        ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )
    from_curator_id = Column(
        String, ForeignKey("curators.id", ondelete="SET NULL"), nullable=True
    )
    to_curator_id = Column(
        String, ForeignKey("curators.id", ondelete="SET NULL"), nullable=True
    )
    assigned_by = Column(
        String, ForeignKey("curators.id", ondelete="SET NULL"), nullable=True
    )
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    metadata_ = Column("metadata", JSON, nullable=True)

    __table_args__ = (PrimaryKeyConstraint("id"),)
