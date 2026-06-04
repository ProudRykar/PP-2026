from abc import ABC, abstractmethod
import logging
from typing import AsyncGenerator, Optional, List
from src.core.models import Message

logger = logging.getLogger(__name__)


class MessageEngine(ABC):
    """Абстрактный базовый класс для всех движков сообщений"""

    @abstractmethod
    async def start(self) -> None:
        """Запустить движок и начать прослушивание сообщений"""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Остановить движок и освободить ресурсы"""
        pass

    @abstractmethod
    async def send_message(self, recipient: str, content: str, **kwargs) -> str:
        """
        Отправить сообщение через этот канал
        Возвращает: message_id отправленного сообщения
        """
        pass

    @abstractmethod
    async def get_incoming(self) -> AsyncGenerator[Message, None]:
        """Асинхронный генератор, возвращающий входящие сообщения"""
        pass

    @property
    @abstractmethod
    def channel_type(self) -> str:
        """Вернуть идентификатор типа канала"""
        pass

    @property
    @abstractmethod
    def is_running(self) -> bool:
        """Вернуть True, если движок сейчас запущен"""
        pass


class EngineFactory(ABC):
    """Абстрактная фабрика для создания движков сообщений"""

    @abstractmethod
    def create_engine(self, config: dict, repository=None) -> MessageEngine:
        """Создать и вернуть экземпляр движка"""
        pass

    @abstractmethod
    def get_supported_channel(self) -> str:
        """Вернуть тип канала, который поддерживает эта фабрика"""
        pass


class MessageRepository(ABC):
    """Абстрактный репозиторий для хранения сообщений"""

    @abstractmethod
    async def save_message(self, message: Message) -> None:
        """Сохранить сообщение в базу данных"""
        pass

    @abstractmethod
    async def get_messages(
        self,
        channel: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Message]:
        """Получить список сообщений с опциональной фильтрацией"""
        pass

    @abstractmethod
    async def get_message_by_id(self, message_id: str) -> Optional[Message]:
        """Получить конкретное сообщение по ID"""
        pass


class PollingService(ABC):
    """Абстрактный сервис для управления опросами движков"""

    @abstractmethod
    async def start_polling(self) -> None:
        """Начать опрос всех зарегистрированных движков"""
        pass

    @abstractmethod
    async def stop_polling(self) -> None:
        """Остановить опрос всех движков"""
        pass

    @abstractmethod
    def register_engine(self, engine: MessageEngine) -> None:
        """Зарегистрировать движок для опроса"""
        pass
