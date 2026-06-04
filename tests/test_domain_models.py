from datetime import datetime, timezone

import pytest

from app.core.domain.models.channel_type import ChannelType
from app.core.domain.models.message import Message
from app.core.errors.message import MessageNotFoundError


def test_message_creation():
    now = datetime.now(timezone.utc)
    msg = Message(
        id="test:1",
        channel=ChannelType.TELEGRAM,
        sender="user1",
        content="hello",
        timestamp=now,
        metadata={"key": "val"},
    )

    assert msg.id == "test:1"
    assert msg.channel == ChannelType.TELEGRAM
    assert msg.sender == "user1"
    assert msg.content == "hello"
    assert msg.timestamp == now
    assert msg.metadata == {"key": "val"}
    assert msg.recipient is None
    assert msg.subject is None


def test_message_with_optional_fields():
    now = datetime.now(timezone.utc)
    msg = Message(
        id="test:2",
        channel=ChannelType.EMAIL,
        sender="alice@example.com",
        content="body",
        timestamp=now,
        metadata={},
        recipient="bob@example.com",
        subject="greetings",
    )

    assert msg.recipient == "bob@example.com"
    assert msg.subject == "greetings"


def test_message_to_dict():
    now = datetime.now(timezone.utc)
    msg = Message(
        id="test:3",
        channel=ChannelType.TELEGRAM,
        sender="user1",
        content="hello",
        timestamp=now,
        metadata={"k": "v"},
    )

    d = msg.to_dict()
    assert d["id"] == "test:3"
    assert d["channel"] == ChannelType.TELEGRAM
    assert d["sender"] == "user1"
    assert d["content"] == "hello"
    assert d["timestamp"] == now.isoformat()
    assert d["metadata"] == {"k": "v"}
    assert d["recipient"] is None
    assert d["subject"] is None


def test_channel_type_constants():
    assert ChannelType.TELEGRAM == "telegram"
    assert ChannelType.EMAIL == "email"
    assert ChannelType.SLACK == "slack"
    assert ChannelType.DISCORD == "discord"
    assert ChannelType.VK == "vk"


def test_message_not_found_error():
    exc = MessageNotFoundError("msg:42")
    assert exc.message_id == "msg:42"
    assert str(exc) == "Message msg:42 not found"


def test_message_not_found_error_is_exception():
    assert issubclass(MessageNotFoundError, Exception)


def test_message_requires_no_defaults():
    with pytest.raises(TypeError):
        Message()


def test_message_default_optional_fields():
    now = datetime.now(timezone.utc)
    msg = Message(
        id="x", channel="tg", sender="u", content="c", timestamp=now, metadata={}
    )
    assert msg.recipient is None
    assert msg.subject is None
