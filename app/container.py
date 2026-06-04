import logging
import punq

from app.adapters.engines.factory import (
    EngineAbstractFactory,
    TelegramEngineFactory,
    EmailEngineFactory,
)
from app.adapters.interfaces.db import DatabaseGateway
from app.adapters.interfaces.message_repository import MessageRepository
from app.adapters.interfaces.polling_service import PollingService
from app.adapters.gateways.postgres import PostgresDatabaseGateway
from app.adapters.repositories.postgres.repository import PostgresMessageRepository
from app.core.services.message_service import MessageService
from app.core.services.polling_service import PollingOrchestrator

logger = logging.getLogger(__name__)

_container: punq.Container = None


def get_container() -> punq.Container:
    global _container
    if _container is None:
        _container = configure_container()
    return _container


def configure_container() -> punq.Container:
    container = punq.Container()

    container.register(EngineAbstractFactory, scope=punq.Scope.singleton)

    container.register(TelegramEngineFactory, instance=TelegramEngineFactory())
    container.register(EmailEngineFactory, instance=EmailEngineFactory())

    container.register(
        DatabaseGateway, PostgresDatabaseGateway, scope=punq.Scope.singleton
    )

    container.register(
        MessageRepository, PostgresMessageRepository, scope=punq.Scope.singleton
    )

    container.register(PollingService, PollingOrchestrator, scope=punq.Scope.singleton)

    container.register(MessageService)

    logger.info("DI container configured")
    return container


def initialize_factories(container: punq.Container) -> EngineAbstractFactory:
    abstract_factory = container.resolve(EngineAbstractFactory)

    telegram_factory = container.resolve(TelegramEngineFactory)
    abstract_factory.register_factory(telegram_factory)

    email_factory = container.resolve(EmailEngineFactory)
    abstract_factory.register_factory(email_factory)

    logger.info("All engine factories initialized")
    return abstract_factory
