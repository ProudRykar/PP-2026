from abc import ABC, abstractmethod

from app.adapters.interfaces.message_engine import MessageEngine


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
