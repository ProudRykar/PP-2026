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


class SenderModel(Base):
    __tablename__ = "senders"

    id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SenderIdentityModel(Base):
    __tablename__ = "sender_identities"

    id = Column(String, primary_key=True)
    sender_id = Column(
        String, ForeignKey("senders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    channel = Column(String(50), nullable=False)
    address = Column(String(255), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("id"),)


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    channel = Column(String(50), nullable=False, index=True)
    sender_id = Column(
        String, ForeignKey("senders.id", ondelete="SET NULL"), nullable=True, index=True
    )
    recipient = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), nullable=False, server_default="text")
    subject = Column(String(500), nullable=True)
    parent_id = Column(String, nullable=True, index=True)
    curator_id = Column(String, nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (PrimaryKeyConstraint("id"),)
