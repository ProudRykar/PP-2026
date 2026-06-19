import pytest

from app.core.domain.models.client import ChannelIdentity
from app.core.services.client_service import ClientService

from .conftest import MockClientRepository, make_client


@pytest.fixture
def repo():
    return MockClientRepository()


@pytest.fixture
def service(repo):
    return ClientService(repo)


@pytest.mark.asyncio
async def test_get_or_create_client_new(service, repo):
    client = await service.get_or_create_client(
        channel="telegram",
        external_id="999",
        name="New User",
        username="newuser",
    )

    assert client.id.startswith("client:")
    assert client.name == "New User"
    assert len(client.channels) == 1
    assert client.channels[0].channel == "telegram"
    assert client.channels[0].external_id == "999"
    assert client.channels[0].username == "newuser"
    assert repo._clients[client.id] is client


@pytest.mark.asyncio
async def test_get_or_create_client_existing(service, repo):
    existing = make_client(
        client_id="client:existing",
        name="Existing",
    )
    await repo.save(existing)

    client = await service.get_or_create_client(
        channel="telegram",
        external_id="12345",
        name="Existing",
        username="testuser",
    )

    assert client.id == "client:existing"
    assert client.name == "Existing"


@pytest.mark.asyncio
async def test_get_or_create_client_adds_channel_via_email_fallback(service, repo):
    existing = make_client(
        client_id="client:multi",
        name="Multi",
        email="user@example.com",
        channels=[ChannelIdentity(channel="telegram", external_id="tg_123")],
    )
    await repo.save(existing)

    client = await service.get_or_create_client(
        channel="email",
        external_id="user@example.com",
        name="Multi",
    )

    assert len(client.channels) == 2
    assert any(ch.channel == "telegram" for ch in client.channels)
    assert any(
        ch.channel == "email" and ch.external_id == "user@example.com"
        for ch in client.channels
    )


@pytest.mark.asyncio
async def test_find_by_email_fallback(service, repo):
    client = make_client(
        client_id="client:byemail",
        name="Email Client",
        channels=[ChannelIdentity(channel="email", external_id="user@example.com")],
    )
    await repo.save(client)

    result = await service.get_or_create_client(
        channel="email",
        external_id="user@example.com",
        name="Email Client",
    )

    assert result.id == "client:byemail"


@pytest.mark.asyncio
async def test_get_client(service, repo):
    existing = make_client(client_id="client:get")
    await repo.save(existing)

    result = await service.get_client("client:get")
    assert result is not None
    assert result.id == "client:get"

    missing = await service.get_client("client:nonexistent")
    assert missing is None


@pytest.mark.asyncio
async def test_update_client(service, repo):
    existing = make_client(client_id="client:update", name="Old Name")
    await repo.save(existing)

    updated = await service.update_client(
        "client:update", {"name": "New Name", "phone": "+7999"}
    )
    assert updated.name == "New Name"
    assert updated.phone == "+7999"


@pytest.mark.asyncio
async def test_update_client_not_found(service):
    with pytest.raises(ValueError, match="client:nonexistent"):
        await service.update_client("client:nonexistent", {"name": "X"})


@pytest.mark.asyncio
async def test_add_channel_to_client(service, repo):
    existing = make_client(client_id="client:addch")
    await repo.save(existing)

    result = await service.add_channel_to_client(
        "client:addch", "email", "new@example.com", display_name="New Email"
    )
    assert len(result.channels) == 2
    assert any(
        ch.channel == "email" and ch.external_id == "new@example.com"
        for ch in result.channels
    )


@pytest.mark.asyncio
async def test_add_channel_to_client_duplicate(service, repo):
    existing = make_client(client_id="client:dup")
    await repo.save(existing)

    result = await service.add_channel_to_client("client:dup", "telegram", "12345")
    assert len(result.channels) == 1  # not duplicated


@pytest.mark.asyncio
async def test_add_channel_to_client_not_found(service):
    with pytest.raises(ValueError):
        await service.add_channel_to_client("client:nonexistent", "telegram", "999")


@pytest.mark.asyncio
async def test_find_by_channel(service, repo):
    existing = make_client(client_id="client:find")
    await repo.save(existing)

    result = await service.find_by_channel("telegram", "12345")
    assert result is not None
    assert result.id == "client:find"

    missing = await service.find_by_channel("telegram", "nonexistent")
    assert missing is None


@pytest.mark.asyncio
async def test_get_all_clients(service, repo):
    c1 = make_client(client_id="client:a", name="A")
    c2 = make_client(client_id="client:b", name="B")
    await repo.save(c1)
    await repo.save(c2)

    all_clients = await service.get_all_clients()
    assert len(all_clients) == 2
