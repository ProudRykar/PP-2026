import pytest
from src.core.models import Message, ChannelType
from datetime import datetime


def test_message_creation():
    """Тестирование создания объекта Message и его методов"""
    msg = Message(
        id="test:123",
        channel=ChannelType.TELEGRAM,
        sender="user123",
        content="Hello, world!",
        timestamp=datetime.now(),
        metadata={"test": True}
    )
    
    assert msg.id == "test:123"
    assert msg.channel == ChannelType.TELEGRAM
    assert msg.sender == "user123"
    assert msg.content == "Hello, world!"
    assert msg.to_dict()["channel"] == ChannelType.TELEGRAM


def test_channel_types():
    """Тестирование наличия всех каналов в ChannelType"""
    assert ChannelType.TELEGRAM == "telegram"
    assert ChannelType.EMAIL == "email"
    assert ChannelType.SLACK == "slack"
    assert ChannelType.DISCORD == "discord"
    assert ChannelType.VK == "vk"


@pytest.mark.asyncio
async def test_message_service():
    """Тестирование возможности импорта и создания экземпляра MessageService"""
    from src.services.message_service import MessageService
    from src.infrastructure.repository import PostgresMessageRepository
    
    repo = PostgresMessageRepository()
    service = MessageService(repo)
    
    assert service is not None
