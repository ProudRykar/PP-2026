import logging
from typing import List, Optional
from src.core.interfaces import MessageRepository
from src.core.models import Message

logger = logging.getLogger(__name__)


class MessageService:
    """Сервис для управления сообщениями"""

    def __init__(self, repository: MessageRepository):
        self._repository = repository

    async def save_message(self, message: Message) -> None:
        """Сохранить сообщение"""
        await self._repository.save_message(message)
        logger.info(f"Сообщение сохранено: {message.id}")

    async def get_messages(
        self,
        channel: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Message]:
        """Получить список сообщений с возможностью фильтрации"""
        return await self._repository.get_messages(
            channel=channel,
            limit=limit,
            offset=offset
        )

    async def get_message(self, message_id: str) -> Optional[Message]:
        """Получить сообщение по его ID"""
        return await self._repository.get_message_by_id(message_id)

    async def reply_to_message(
        self,
        original_message: Message,
        content: str
    ) -> None:
        """Ответить на сообщение (Нереализовано)"""
        logger.info(f"Ответ на сообщение {original_message.id}: {content}")
        # Здесь будет логика отправки через соответствующий движок
