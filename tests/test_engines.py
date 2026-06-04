import pytest

from app.adapters.engines.base import BaseEngine
from app.adapters.engines.factory import (
    EngineAbstractFactory,
    TelegramEngineFactory,
    EmailEngineFactory,
)
from app.core.domain.models.channel_type import ChannelType


class _ConcreteEngine(BaseEngine):
    async def send_message(self, recipient: str, content: str, **kwargs) -> str:
        return "mock_id"


@pytest.mark.asyncio
async def test_base_engine_start_stop():
    engine = _ConcreteEngine("test")
    assert engine.is_running is False

    await engine.start()
    assert engine.is_running is True

    await engine.stop()
    assert engine.is_running is False


def test_base_engine_channel_type():
    engine = _ConcreteEngine("custom")
    assert engine.channel_type == "custom"


def test_base_engine_generate_message_id():
    engine = _ConcreteEngine("test")
    mid = engine._generate_message_id("42")
    assert mid == "test:42"


@pytest.mark.asyncio
async def test_base_engine_get_incoming_empty():
    engine = _ConcreteEngine("test")
    await engine.start()
    results = []
    async for msg in engine.get_incoming():
        results.append(msg)

    assert len(results) == 0
    await engine.stop()


@pytest.mark.asyncio
async def test_base_engine_get_incoming_not_running():
    engine = _ConcreteEngine("test")
    results = []
    async for msg in engine.get_incoming():
        results.append(msg)

    assert len(results) == 0


def test_telegram_factory_supported_channel():
    factory = TelegramEngineFactory()
    assert factory.get_supported_channel() == ChannelType.TELEGRAM


def test_telegram_factory_missing_token():
    factory = TelegramEngineFactory()
    with pytest.raises(ValueError, match="Telegram token is required"):
        factory.create_engine({})


def test_telegram_factory_create():
    factory = TelegramEngineFactory()
    engine = factory.create_engine({"token": "abc:123"})
    assert engine.channel_type == ChannelType.TELEGRAM


def test_email_factory_supported_channel():
    factory = EmailEngineFactory()
    assert factory.get_supported_channel() == ChannelType.EMAIL


def test_email_factory_missing_config():
    factory = EmailEngineFactory()
    with pytest.raises(ValueError):
        factory.create_engine({})


def test_email_factory_create():
    factory = EmailEngineFactory()
    engine = factory.create_engine(
        {"host": "imap.example.com", "port": 993, "user": "u", "password": "p"}
    )
    assert engine.channel_type == ChannelType.EMAIL


def test_abstract_factory_register_and_create():
    af = EngineAbstractFactory()
    af.register_factory(TelegramEngineFactory())

    engine = af.create_engine(ChannelType.TELEGRAM, {"token": "abc"})
    assert engine.channel_type == ChannelType.TELEGRAM


def test_abstract_factory_unregistered_channel():
    af = EngineAbstractFactory()
    with pytest.raises(ValueError, match="No factory registered"):
        af.create_engine("unknown", {})


def test_abstract_factory_supported_channels():
    af = EngineAbstractFactory()
    assert af.get_supported_channels() == []

    af.register_factory(TelegramEngineFactory())
    assert ChannelType.TELEGRAM in af.get_supported_channels()
