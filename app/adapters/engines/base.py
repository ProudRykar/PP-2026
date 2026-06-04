import logging
from typing import AsyncGenerator

from app.core.ports.message_engine import MessageEngine
from app.core.domain.models.message import Message

logger = logging.getLogger(__name__)


class BaseEngine(MessageEngine):
    def __init__(self, channel_type: str):
        self._channel_type = channel_type
        self._running = False

    async def start(self) -> None:
        self._running = True
        logger.info(f"{self._channel_type} engine started")

    async def stop(self) -> None:
        self._running = False
        logger.info(f"{self._channel_type} engine stopped")

    async def get_incoming(self) -> AsyncGenerator[Message, None]:
        if not self._running:
            return
        if False:
            yield

    @property
    def channel_type(self) -> str:
        return self._channel_type

    @property
    def is_running(self) -> bool:
        return self._running

    def _generate_message_id(self, original_id: str) -> str:
        return f"{self._channel_type}:{original_id}"
