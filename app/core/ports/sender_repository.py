from abc import ABC, abstractmethod
from typing import Optional

from app.core.domain.models.sender import Sender


class SenderRepository(ABC):
    @abstractmethod
    async def save(self, sender: Sender) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, sender_id: str) -> Optional[Sender]:
        pass

    @abstractmethod
    async def find_by_identity(self, channel: str, address: str) -> Optional[Sender]:
        pass

    @abstractmethod
    async def find_all(self) -> list[Sender]:
        pass
