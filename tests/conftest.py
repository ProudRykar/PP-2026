from datetime import datetime
from typing import AsyncIterator, Optional, List
from dataclasses import dataclass, field

from app.core.domain.models.message import Message
from app.core.domain.models.channel_type import ChannelType
from app.adapters.interfaces.message_repository import MessageRepository
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
    sender: str = "user1",
    content: str = "hello",
    **kwargs,
) -> Message:
    return Message(
        id=id,
        channel=channel,
        sender=sender,
        content=content,
        timestamp=kwargs.pop("timestamp", datetime.now()),
        metadata=kwargs.pop("metadata", {}),
        **kwargs,
    )


def make_message_service(
    repo: Optional[MockMessageRepository] = None,
) -> MessageService:
    return MessageService(repo or MockMessageRepository())
