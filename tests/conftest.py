from datetime import datetime, timezone
from typing import AsyncIterator, Optional, List
from dataclasses import dataclass, field

from app.core.ports.polling_service import (
    PollingService as AbstractPollingService,
)
from app.core.domain.models.message import Message
from app.core.domain.models.channel_type import ChannelType
from app.core.domain.models.client import Client, ChannelIdentity
from app.core.ports.message_repository import MessageRepository
from app.core.ports.client_repository import ClientRepository
from app.core.services.message_service import MessageService


@dataclass
class MockMessageRepository(MessageRepository):
    _messages: dict[str, Message] = field(default_factory=dict)

    async def save_message(self, message: Message) -> None:
        self._messages[message.id] = message

    async def get_messages(
        self,
        channel: Optional[str] = None,
        sender_id: Optional[str] = None,
        curator_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Message]:
        msgs = list(self._messages.values())
        if channel:
            msgs = [m for m in msgs if m.channel == channel]
        if sender_id:
            msgs = [m for m in msgs if m.sender_id == sender_id]
        if curator_id:
            msgs = [m for m in msgs if m.curator_id == curator_id]
        return msgs[offset : offset + limit]

    async def get_message_by_id(self, message_id: str) -> Optional[Message]:
        return self._messages.get(message_id)

    async def update_curator(self, message_id: str, curator_id: Optional[str]) -> None:
        msg = self._messages.get(message_id)
        if msg:
            msg.curator_id = curator_id


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
        self,
        channel: str,
        recipient: str,
        content: str,
        subject: str | None = None,
        **kwargs,
    ) -> str | None:
        self._last_reply = (channel, recipient, content)
        return "mock_reply_id"


def make_message_service(
    repo: Optional[MockMessageRepository] = None,
) -> MessageService:
    return MessageService(repo or MockMessageRepository())


@dataclass
class MockClientRepository(ClientRepository):
    _clients: dict[str, Client] = field(default_factory=dict)

    async def save(self, client: Client) -> None:
        self._clients[client.id] = client

    async def get_by_id(self, client_id: str) -> Optional[Client]:
        return self._clients.get(client_id)

    async def find_by_channel(self, channel: str, external_id: str) -> Optional[Client]:
        for client in self._clients.values():
            for ch in client.channels:
                if ch.channel == channel and ch.external_id == external_id:
                    return client
        return None

    async def find_by_email(self, email: str) -> Optional[Client]:
        for client in self._clients.values():
            if client.email == email:
                return client
            for ch in client.channels:
                if ch.channel == "email" and ch.external_id == email:
                    return client
        return None

    async def update(self, client: Client) -> None:
        self._clients[client.id] = client

    async def get_all(self) -> list[Client]:
        return list(self._clients.values())


def make_client(
    client_id: str = "client:test",
    name: str = "Test Client",
    channels: Optional[list[ChannelIdentity]] = None,
    **kwargs,
) -> Client:
    return Client(
        id=client_id,
        name=name,
        channels=channels
        or [
            ChannelIdentity(
                channel="telegram",
                external_id="12345",
                username="testuser",
                display_name="Test",
            ),
        ],
        created_at=kwargs.pop("created_at", datetime.now(timezone.utc)),
        last_interaction=kwargs.pop("last_interaction", datetime.now(timezone.utc)),
        **kwargs,
    )
