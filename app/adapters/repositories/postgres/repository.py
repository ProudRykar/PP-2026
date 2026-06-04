import logging
from typing import List, Optional, Dict, Any, cast
from datetime import datetime
from sqlalchemy import select, desc

from app.adapters.interfaces.message_repository import MessageRepository
from app.core.domain.models.message import Message
from app.adapters.interfaces.db import DatabaseGateway
from app.adapters.repositories.postgres.models import MessageModel

logger = logging.getLogger(__name__)


class PostgresMessageRepository(MessageRepository):
    def __init__(self, db: DatabaseGateway):
        self._db = db

    async def save_message(self, message: Message) -> None:
        async with self._db.get_session() as session:
            msg_model = MessageModel(
                id=message.id,
                channel=message.channel,
                sender=message.sender,
                recipient=message.recipient,
                content=message.content,
                subject=message.subject,
                timestamp=message.timestamp,
                metadata_=message.metadata,
            )
            session.add(msg_model)
            logger.debug(f"Message saved: {message.id}")

    async def get_messages(
        self, channel: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[Message]:
        async with self._db.get_session() as session:
            query = select(MessageModel).order_by(desc(MessageModel.timestamp))

            if channel:
                query = query.where(MessageModel.channel == channel)

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
            sender=cast(str, m.sender),
            recipient=cast(Optional[str], m.recipient),
            content=cast(str, m.content),
            subject=cast(Optional[str], m.subject),
            timestamp=cast(datetime, m.timestamp),
            metadata=cast(Dict[str, Any], m.metadata_ if m.metadata_ else {}),
        )
