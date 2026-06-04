import pytest

from app.core.errors.message import MessageNotFoundError

from .conftest import make_message, make_message_service, MockMessageRepository


@pytest.mark.asyncio
async def test_save_message():
    repo = MockMessageRepository()
    service = make_message_service(repo)
    msg = make_message()

    await service.save_message(msg)

    assert await repo.get_message_by_id(msg.id) is msg


@pytest.mark.asyncio
async def test_get_messages_returns_all():
    repo = MockMessageRepository()
    service = make_message_service(repo)
    msgs = [make_message(id=f"test:{i}") for i in range(3)]
    for m in msgs:
        await service.save_message(m)

    result = await service.get_messages()

    assert len(result) == 3


@pytest.mark.asyncio
async def test_get_messages_filter_by_channel():
    repo = MockMessageRepository()
    service = make_message_service(repo)
    await service.save_message(make_message(id="t:1", channel="telegram"))
    await service.save_message(make_message(id="e:1", channel="email"))

    tg = await service.get_messages(channel="telegram")
    assert len(tg) == 1
    assert tg[0].id == "t:1"


@pytest.mark.asyncio
async def test_get_messages_with_limit_and_offset():
    repo = MockMessageRepository()
    service = make_message_service(repo)
    for i in range(10):
        await service.save_message(make_message(id=f"test:{i}"))

    result = await service.get_messages(limit=3, offset=5)
    assert len(result) == 3


@pytest.mark.asyncio
async def test_get_existing_message():
    repo = MockMessageRepository()
    service = make_message_service(repo)
    msg = make_message(id="find:me")
    await service.save_message(msg)

    found = await service.get_message("find:me")
    assert found is msg


@pytest.mark.asyncio
async def test_get_nonexistent_message_returns_none():
    service = make_message_service()
    found = await service.get_message("no:such")
    assert found is None


@pytest.mark.asyncio
async def test_reply_to_existing_message():
    repo = MockMessageRepository()
    service = make_message_service(repo)
    msg = make_message(id="orig:1")
    await service.save_message(msg)

    await service.reply_to_message("orig:1", "reply content")


@pytest.mark.asyncio
async def test_reply_to_nonexistent_message_raises():
    service = make_message_service()

    with pytest.raises(MessageNotFoundError) as exc:
        await service.reply_to_message("no:such", "content")

    assert exc.value.message_id == "no:such"
