from sqlalchemy import Column, String, Text, DateTime, JSON, PrimaryKeyConstraint
from sqlalchemy.sql import func

from app.adapters.gateways.postgres import Base


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    channel = Column(String(50), nullable=False, index=True)
    sender = Column(String(255), nullable=False)
    recipient = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    subject = Column(String(500), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (PrimaryKeyConstraint("id"),)
