import logging
from typing import List, Optional, Dict, Any, cast
from datetime import datetime
from sqlalchemy import select, desc

from app.core.ports.message_repository import MessageRepository
from app.core.domain.models.message import Message
from app.core.domain.models.channel_type import MessageType
from app.core.ports.db import DatabaseGateway
from app.adapters.repositories.postgres.models import MessageModel, SenderModel

logger = logging.getLogger(__name__)


class PostgresMessageRepository(MessageRepository):
    def __init__(self, db: DatabaseGateway):
        self._db = db

    async def save_message(self, message: Message) -> None:
        async with self._db.get_session() as session:
            existing = await session.execute(
                select(SenderModel).where(SenderModel.id == message.sender_id)
            )
            if not existing.scalar_one_or_none():
                sender = SenderModel(id=message.sender_id, name=message.sender_id)
                session.add(sender)
                await session.flush()

            msg_model = MessageModel(
                id=message.id,
                channel=message.channel,
                sender_id=message.sender_id,
                recipient=message.recipient,
                content=message.content,
                message_type=message.message_type.value,
                subject=message.subject,
                parent_id=message.parent_id,
                timestamp=message.timestamp,
                metadata_=message.metadata,
            )
            session.add(msg_model)
            logger.debug(f"Message saved: {message.id}")

    async def get_messages(
        self,
        channel: Optional[str] = None,
        sender_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Message]:
        async with self._db.get_session() as session:
            query = select(MessageModel).order_by(desc(MessageModel.timestamp))

            if channel:
                query = query.where(MessageModel.channel == channel)
            if sender_id:
                query = query.where(MessageModel.sender_id == sender_id)

            query = query.limit(limit).offset(offset)
            result = await session.execute(query)
            msg_models = result.scalars().all()

            return [self._to_message(m) for m in msg_models]

    async def get_message_by_id(self, message_id: str) -> Optional[Message]:
        async with self._db.get_session() as session:
            result = await session.execute(
                select(MessageModel).where(MessageModel.id == message_id)
            )
            msg_model = result.scalar_one_or_none()
            return self._to_message(msg_model) if msg_model else None

    def _to_message(self, m: MessageModel) -> Message:
        return Message(
            id=cast(str, m.id),
            channel=cast(str, m.channel),
            sender_id=cast(str, m.sender_id) if m.sender_id else "",
            recipient=cast(Optional[str], m.recipient),
            content=cast(str, m.content),
            subject=cast(Optional[str], m.subject),
            parent_id=cast(Optional[str], m.parent_id),
            timestamp=cast(datetime, m.timestamp),
            message_type=MessageType(cast(str, m.message_type))
            if m.message_type
            else MessageType.TEXT,
            metadata=cast(Dict[str, Any], m.metadata_ if m.metadata_ else {}),
        )
