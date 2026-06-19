import logging
from typing import List, Optional

from app.core.domain.models.message import Message
from app.core.ports.message_repository import MessageRepository

logger = logging.getLogger(__name__)


class MessageService:
    def __init__(self, repository: MessageRepository):
        self._repository = repository

    async def save_message(self, message: Message) -> None:
        await self._repository.save_message(message)
        logger.info(f"Message saved: {message.id}")

    async def get_messages(
        self,
        channel: Optional[str] = None,
        sender_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Message]:
        return await self._repository.get_messages(
            channel=channel, sender_id=sender_id, limit=limit, offset=offset
        )

    async def get_message(self, message_id: str) -> Optional[Message]:
        return await self._repository.get_message_by_id(message_id)

    async def reply_to_message(self, message_id: str, content: str) -> Message:
        original = await self._repository.get_message_by_id(message_id)
        if not original:
            from app.core.errors.message import MessageNotFoundError

            raise MessageNotFoundError(message_id)
        logger.info(f"Reply to {message_id}: {content}")
        return original
