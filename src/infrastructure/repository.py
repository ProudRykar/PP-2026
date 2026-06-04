import logging
from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.interfaces import MessageRepository
from src.core.models import Message
from src.infrastructure.models import MessageModel
from src.infrastructure.database import get_async_sessionmaker

logger = logging.getLogger(__name__)


class PostgresMessageRepository(MessageRepository):
    """Имплементация репозитория сообщений, использующая PostgreSQL через SQLAlchemy ORM"""

    def __init__(self):
        pass

    async def save_message(self, message: Message) -> None:
        """Сохранить сообщение в базе данных"""
        async_session = get_async_sessionmaker()
        async with async_session() as session:
            msg_model = MessageModel(
                id=message.id,
                channel=message.channel,
                sender=message.sender,
                recipient=message.recipient,
                content=message.content,
                subject=message.subject,
                timestamp=message.timestamp,
                metadata_=message.metadata
            )
            session.add(msg_model)
            await session.commit()
            logger.debug(f"Сохранено сообщение: {message.id}")

    async def get_messages(
        self,
        channel: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Message]:
        """Получить список сообщений с возможностью фильтрации"""
        async_session = get_async_sessionmaker()
        async with async_session() as session:
            query = select(MessageModel).order_by(desc(MessageModel.timestamp))

            if channel:
                query = query.where(MessageModel.channel == channel)

            query = query.limit(limit).offset(offset)
            result = await session.execute(query)
            msg_models = result.scalars().all()

            return [
                Message(
                    id=m.id,
                    channel=m.channel,
                    sender=m.sender,
                    recipient=m.recipient,
                    content=m.content,
                    subject=m.subject,
                    timestamp=m.timestamp,
                    metadata=m.metadata_ or {}
                )
                for m in msg_models
            ]

    async def get_message_by_id(
        self, 
        message_id: str
    ) -> Optional[Message]:
        """Получить сообщение по его ID"""
        async_session = get_async_sessionmaker()
        async with async_session() as session:
            result = await session.execute(
                select(MessageModel).where(MessageModel.id == message_id)
            )
            msg_model = result.scalar_one_or_none()

            if not msg_model:
                return None

            return Message(
                id=msg_model.id,
                channel=msg_model.channel,
                sender=msg_model.sender,
                recipient=msg_model.recipient,
                content=msg_model.content,
                subject=msg_model.subject,
                timestamp=msg_model.timestamp,
                metadata=msg_model.metadata_ or {}
            )
