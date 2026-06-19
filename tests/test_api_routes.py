import pytest
from litestar import Litestar
from litestar.di import Provide
from litestar.testing import TestClient

from app.api.routers.routes import MessageController
from app.api.routers.health import HealthController
from app.api.exceptions.handlers import EXCEPTION_HANDLERS
from app.core.domain.models.channel_type import ChannelType

from .conftest import make_message, MockMessageRepository, MockPollingService


@pytest.fixture
def repo():
    return MockMessageRepository()


@pytest.fixture
def mock_service(repo):
    from app.core.services.message_service import MessageService

    return MessageService(repo)


@pytest.fixture
def mock_polling():
    return MockPollingService()


@pytest.fixture
def test_app(mock_service, mock_polling):
    async def provide_service():
        return mock_service

    async def provide_polling():
        return mock_polling

    app = Litestar(
        route_handlers=[MessageController, HealthController],
        dependencies={
            "service": Provide(provide_service),
            "polling": Provide(provide_polling),
        },
        exception_handlers=EXCEPTION_HANDLERS,
    )
    return app


@pytest.fixture
def client(test_app):
    return TestClient(test_app)


def test_health_returns_200(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"


def test_get_messages_empty(client):
    resp = client.get("/api/messages")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_messages_with_data(client, repo, mock_service):
    msg = make_message(id="api:1")
    repo._messages[msg.id] = msg

    resp = client.get("/api/messages")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == "api:1"


def test_get_messages_filter_by_channel(client, repo):
    repo._messages["t:1"] = make_message(id="t:1", channel=ChannelType.TELEGRAM)
    repo._messages["e:1"] = make_message(id="e:1", channel=ChannelType.EMAIL)

    resp = client.get("/api/messages?channel=email")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == "e:1"


def test_get_message_found(client, repo):
    repo._messages["find:me"] = make_message(id="find:me")

    resp = client.get("/api/messages/find:me")
    assert resp.status_code == 200
    assert resp.json()["id"] == "find:me"


def test_get_message_not_found(client):
    resp = client.get("/api/messages/no:such")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Message no:such not found"


def test_get_channels(client):
    resp = client.get("/api/channels")
    assert resp.status_code == 200
    channels = resp.json()["channels"]
    assert ChannelType.TELEGRAM in channels
    assert ChannelType.EMAIL in channels


def test_reply_to_message_success(client, repo):
    repo._messages["orig:1"] = make_message(id="orig:1")

    resp = client.post(
        "/api/messages/reply",
        json={"message_id": "orig:1", "content": "reply text"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"


def test_reply_to_nonexistent_message(client):
    resp = client.post(
        "/api/messages/reply",
        json={"message_id": "no:such", "content": "reply"},
    )
    assert resp.status_code == 404
