from sqlalchemy import (
    Column,
    String,
    DateTime,
    JSON,
    ForeignKey,
    PrimaryKeyConstraint,
)
from sqlalchemy.sql import func

from app.adapters.gateways.postgres import Base


class ClientModel(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False, server_default="")
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_interaction = Column(DateTime(timezone=True), nullable=True)
    curator_id = Column(String, ForeignKey("curators.id", ondelete="SET NULL"), nullable=True, index=True)

    __table_args__ = (PrimaryKeyConstraint("id"),)


class ClientChannelModel(Base):
    __tablename__ = "client_channels"

    id = Column(String, primary_key=True)
    client_id = Column(
        String, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    channel = Column(String(50), nullable=False)
    external_id = Column(String(255), nullable=False)
    username = Column(String(255), nullable=True)
    display_name = Column(String(255), nullable=True)

    __table_args__ = (PrimaryKeyConstraint("id"),)
