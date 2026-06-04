import logging
from abc import abstractmethod
from typing import AsyncGenerator
from src.core.interfaces import MessageEngine
from src.core.models import Message

logger = logging.getLogger(__name__)


class BaseEngine(MessageEngine):
    """Базовая реализация с общей функциональностью для всех движков"""

    def __init__(self, channel_type: str):
        self._channel_type = channel_type
        self._running = False
        self._engine = None

    async def start(self) -> None:
        """Запустить движок — базовая реализация"""
        self._running = True
        logger.info(f"{self._channel_type} engine started")

    async def stop(self) -> None:
        """Остановить движок — базовая реализация"""
        self._running = False
        logger.info(f"{self._channel_type} engine stopped")

    async def get_incoming(self) -> AsyncGenerator[Message, None]:
        """Переопределите в подклассах для реализации получения сообщений"""
        if not self._running:
            return
        yield 

    @property
    def channel_type(self) -> str:
        return self._channel_type

    @property
    def is_running(self) -> bool:
        return self._running

    def _generate_message_id(self, original_id: str) -> str:
        """Сгенерировать унифицированный идентификатор сообщения из специфичного для канала ID"""
        return f"{self._channel_type}:{original_id}"