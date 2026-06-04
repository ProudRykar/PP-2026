from abc import ABC, abstractmethod

from app.core.ports.message_engine import MessageEngine


class PollingService(ABC):
    @abstractmethod
    async def start_polling(self) -> None:
        pass

    @abstractmethod
    async def stop_polling(self) -> None:
        pass

    @abstractmethod
    def register_engine(self, engine: MessageEngine) -> None:
        pass

    @abstractmethod
    async def send_reply(
        self, channel: str, recipient: str, content: str, subject: str | None = None
    ) -> str | None:
        pass
