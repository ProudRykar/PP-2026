import pytest
from litestar import Litestar
from litestar.di import Provide
from litestar.testing import TestClient

from app.api.routers.client_routes import ClientController
from app.core.domain.models.client import ChannelIdentity

from .conftest import MockClientRepository, make_client


@pytest.fixture
def repo():
    return MockClientRepository()


@pytest.fixture
def client_service(repo):
    from app.core.services.client_service import ClientService

    return ClientService(repo)


@pytest.fixture
def test_app(client_service):
    async def provide_client_service():
        return client_service

    app = Litestar(
        route_handlers=[ClientController],
        dependencies={
            "client_service": Provide(provide_client_service),
        },
    )
    return app


@pytest.fixture
def client(test_app):
    return TestClient(test_app)


def test_list_clients_empty(client):
    resp = client.get("/api/clients")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_clients_with_data(client, repo):
    repo._clients["client:1"] = make_client(client_id="client:1", name="Alice")
    repo._clients["client:2"] = make_client(client_id="client:2", name="Bob")

    resp = client.get("/api/clients")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    names = {c["name"] for c in data}
    assert names == {"Alice", "Bob"}


def test_get_client_found(client, repo):
    repo._clients["client:found"] = make_client(client_id="client:found", name="Found")

    resp = client.get("/api/clients/client:found")
    assert resp.status_code == 200
    assert resp.json()["id"] == "client:found"
    assert resp.json()["name"] == "Found"


def test_get_client_not_found(client):
    resp = client.get("/api/clients/client:nonexistent")
    assert resp.status_code == 404


def test_find_by_channel_found(client, repo):
    repo._clients["client:ch"] = make_client(
        client_id="client:ch",
        channels=[ChannelIdentity(channel="telegram", external_id="tg_123")],
    )

    resp = client.get("/api/clients/by-channel?channel=telegram&external_id=tg_123")
    assert resp.status_code == 200
    assert resp.json()["id"] == "client:ch"


def test_find_by_channel_not_found(client):
    resp = client.get(
        "/api/clients/by-channel?channel=telegram&external_id=nonexistent"
    )
    assert resp.status_code == 200
    assert resp.json() is None


def test_update_client(client, repo):
    repo._clients["client:upd"] = make_client(client_id="client:upd", name="Old")

    resp = client.put("/api/clients/client:upd", json={"name": "Updated"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated"


def test_update_client_not_found(client):
    resp = client.put("/api/clients/client:nonexistent", json={"name": "X"})
    assert resp.status_code == 500
