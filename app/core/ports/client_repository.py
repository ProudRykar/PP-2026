from abc import ABC, abstractmethod
from typing import Optional

from app.core.domain.models.client import Client


class ClientRepository(ABC):
    @abstractmethod
    async def save(self, client: Client) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, client_id: str) -> Optional[Client]:
        pass

    @abstractmethod
    async def find_by_channel(self, channel: str, external_id: str) -> Optional[Client]:
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[Client]:
        pass

    @abstractmethod
    async def update(self, client: Client) -> None:
        pass

    @abstractmethod
    async def get_all(self) -> list[Client]:
        pass
