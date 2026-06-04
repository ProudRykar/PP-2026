from abc import ABC, abstractmethod

from app.adapters.interfaces.message_engine import MessageEngine


class EngineFactory(ABC):
    @abstractmethod
    def create_engine(self, config: dict) -> MessageEngine:
        pass

    @abstractmethod
    def get_supported_channel(self) -> str:
        pass
