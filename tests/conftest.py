from datetime import datetime
from typing import AsyncIterator, Optional, List
from dataclasses import dataclass, field

from app.core.ports.polling_service import (
    PollingService as AbstractPollingService,
)
from app.core.domain.models.message import Message
from app.core.domain.models.channel_type import ChannelType
from app.core.ports.message_repository import MessageRepository
from app.core.services.message_service import MessageService


@dataclass
class MockMessageRepository(MessageRepository):
    _messages: dict[str, Message] = field(default_factory=dict)

    async def save_message(self, message: Message) -> None:
        self._messages[message.id] = message

    async def get_messages(
        self, channel: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[Message]:
        msgs = list(self._messages.values())
        if channel:
            msgs = [m for m in msgs if m.channel == channel]
        return msgs[offset : offset + limit]

    async def get_message_by_id(self, message_id: str) -> Optional[Message]:
        return self._messages.get(message_id)


class MockEngine:
    def __init__(self, channel: str = ChannelType.TELEGRAM):
        self._channel = channel
        self._running = False
        self._messages: list[Message] = []

    async def start(self) -> None:
        self._running = True

    async def stop(self) -> None:
        self._running = False

    async def send_message(self, recipient: str, content: str, **kwargs) -> str:
        return "mock_id"

    async def get_incoming(self) -> AsyncIterator[Message]:
        for msg in self._messages:
            yield msg

    @property
    def channel_type(self) -> str:
        return self._channel

    @property
    def is_running(self) -> bool:
        return self._running

    def add_message(self, msg: Message) -> None:
        self._messages.append(msg)


def make_message(
    id: str = "test:1",
    channel: str = ChannelType.TELEGRAM,
    sender_id: str = "user1",
    content: str = "hello",
    **kwargs,
) -> Message:
    return Message(
        id=id,
        channel=channel,
        sender_id=sender_id,
        content=content,
        timestamp=kwargs.pop("timestamp", datetime.now()),
        metadata=kwargs.pop("metadata", {}),
        **kwargs,
    )


class MockPollingService(AbstractPollingService):
    def __init__(self):
        self._last_reply: tuple[str, str, str] | None = None

    async def start_polling(self) -> None:
        pass

    async def stop_polling(self) -> None:
        pass

    def register_engine(self, engine) -> None:
        pass

    async def send_reply(
        self, channel: str, recipient: str, content: str, subject: str | None = None
    ) -> str | None:
        self._last_reply = (channel, recipient, content)
        return "mock_reply_id"


def make_message_service(
    repo: Optional[MockMessageRepository] = None,
) -> MessageService:
    return MessageService(repo or MockMessageRepository())
