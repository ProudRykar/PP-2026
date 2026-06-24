import punq

from app.adapters.engines.factory import (
    EngineAbstractFactory,
    TelegramEngineFactory,
    EmailEngineFactory,
)
from app.core.ports.db import DatabaseGateway
from app.core.ports.message_repository import MessageRepository
from app.core.ports.curator_repository import (
    CuratorRepository,
    AssignmentHistoryRepository,
)
from app.core.ports.polling_service import PollingService
from app.core.services.message_service import MessageService
from app.core.services.curator_service import CuratorService
from app.core.services.auth_service import AuthService


def test_configure_container_resolves_all():
    from app.container import configure_container

    container = configure_container()

    assert isinstance(container.resolve(EngineAbstractFactory), EngineAbstractFactory)
    assert isinstance(container.resolve(TelegramEngineFactory), TelegramEngineFactory)
    assert isinstance(container.resolve(EmailEngineFactory), EmailEngineFactory)
    assert isinstance(container.resolve(DatabaseGateway), DatabaseGateway)
    assert isinstance(container.resolve(MessageRepository), MessageRepository)
    assert isinstance(container.resolve(CuratorRepository), CuratorRepository)
    assert isinstance(
        container.resolve(AssignmentHistoryRepository), AssignmentHistoryRepository
    )
    assert isinstance(container.resolve(CuratorService), CuratorService)
    assert isinstance(container.resolve(AuthService), AuthService)
    assert isinstance(container.resolve(PollingService), PollingService)
    assert isinstance(container.resolve(MessageService), MessageService)


def test_configure_container_is_punq():
    from app.container import configure_container

    container = configure_container()
    assert isinstance(container, punq.Container)


def test_initialize_factories():
    from app.container import configure_container, initialize_factories

    container = configure_container()
    abstract_factory = initialize_factories(container)

    assert isinstance(abstract_factory, EngineAbstractFactory)
    supported = abstract_factory.get_supported_channels()
    assert "telegram" in supported
    assert "email" in supported


def test_get_container_singleton():
    from app.container import get_container

    c1 = get_container()
    c2 = get_container()
    assert c1 is c2
