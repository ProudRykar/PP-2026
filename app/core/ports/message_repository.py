from abc import ABC, abstractmethod
from typing import Optional

from app.core.domain.models.message import Message


class MessageRepository(ABC):
    @abstractmethod
    async def save_message(self, message: Message) -> None:
        pass

    @abstractmethod
    async def get_messages(
        self,
        channel: Optional[str] = None,
        sender_id: Optional[str] = None,
        curator_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Message]:
        pass

    @abstractmethod
    async def get_message_by_id(self, message_id: str) -> Optional[Message]:
        pass

    @abstractmethod
    async def update_curator(self, message_id: str, curator_id: Optional[str]) -> None:
        pass
