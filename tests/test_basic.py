import pytest
from app.core.domain.models.message import Message
from app.core.domain.models.channel_type import ChannelType
from datetime import datetime


def test_message_creation():
    msg = Message(
        id="test:123",
        channel=ChannelType.TELEGRAM,
        sender_id="user123",
        content="Hello, world!",
        timestamp=datetime.now(),
        metadata={"test": True},
    )

    assert msg.id == "test:123"
    assert msg.channel == ChannelType.TELEGRAM
    assert msg.sender_id == "user123"
    assert msg.content == "Hello, world!"
    assert msg.to_dict()["channel"] == ChannelType.TELEGRAM


def test_channel_types():
    assert ChannelType.TELEGRAM == "telegram"
    assert ChannelType.EMAIL == "email"
    assert ChannelType.SLACK == "slack"
    assert ChannelType.DISCORD == "discord"
    assert ChannelType.VK == "vk"


@pytest.mark.asyncio
async def test_message_service():
    from app.core.services.message_service import MessageService
    from app.adapters.repositories.postgres.repository import PostgresMessageRepository
    from app.adapters.gateways.postgres import PostgresDatabaseGateway

    db = PostgresDatabaseGateway()
    repo = PostgresMessageRepository(db)
    service = MessageService(repo)

    assert service is not None
