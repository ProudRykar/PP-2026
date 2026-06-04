from abc import ABC, abstractmethod
from typing import AsyncIterator

from app.core.domain.models.message import Message


class MessageEngine(ABC):
    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def stop(self) -> None:
        pass

    @abstractmethod
    async def send_message(self, recipient: str, content: str, **kwargs) -> str:
        pass

    @abstractmethod
    def get_incoming(self) -> AsyncIterator[Message]:
        pass

    @property
    @abstractmethod
    def channel_type(self) -> str:
        pass

    @property
    @abstractmethod
    def is_running(self) -> bool:
        pass
