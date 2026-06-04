import asyncio

import pytest

from app.core.services.polling_service import PollingOrchestrator

from .conftest import (
    make_message,
    make_message_service,
    MockEngine,
    MockMessageRepository,
)


@pytest.mark.asyncio
async def test_register_engine():
    orchestrator = PollingOrchestrator(make_message_service())
    engine = MockEngine()

    orchestrator.register_engine(engine)

    assert len(orchestrator._engines) == 1
    assert orchestrator._engines[0] is engine


@pytest.mark.asyncio
async def test_start_and_stop_polling():
    orchestrator = PollingOrchestrator(make_message_service())
    engine = MockEngine()
    orchestrator.register_engine(engine)

    await orchestrator.start_polling()
    assert engine.is_running is True

    await orchestrator.stop_polling()
    assert engine.is_running is False


@pytest.mark.asyncio
async def test_poll_engine_saves_messages():
    repo = MockMessageRepository()
    service = make_message_service(repo)
    orchestrator = PollingOrchestrator(service)
    engine = MockEngine()
    msg = make_message()
    engine.add_message(msg)
    orchestrator.register_engine(engine)

    await orchestrator.start_polling()
    await asyncio.sleep(0.05)

    saved = await repo.get_message_by_id(msg.id)
    assert saved is msg

    await orchestrator.stop_polling()


@pytest.mark.asyncio
async def test_stop_polling_with_no_engines():
    orchestrator = PollingOrchestrator(make_message_service())
    await orchestrator.stop_polling()


@pytest.mark.asyncio
async def test_multiple_engines():
    repo = MockMessageRepository()
    service = make_message_service(repo)
    orchestrator = PollingOrchestrator(service)
    tg = MockEngine(channel="telegram")
    em = MockEngine(channel="email")
    orchestrator.register_engine(tg)
    orchestrator.register_engine(em)

    await orchestrator.start_polling()
    assert tg.is_running is True
    assert em.is_running is True

    await orchestrator.stop_polling()
    assert tg.is_running is False
    assert em.is_running is False
