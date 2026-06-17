import logging
import punq

from app.adapters.engines.factory import (
    EngineAbstractFactory,
    TelegramEngineFactory,
    EmailEngineFactory,
)
from app.adapters.gateways.s3 import MinioGateway
from app.core.ports.db import DatabaseGateway
from app.core.ports.message_repository import MessageRepository
from app.core.ports.polling_service import PollingService
from app.core.ports.s3 import S3Interface
from app.core.ports.sender_repository import SenderRepository
from app.adapters.gateways.postgres import PostgresDatabaseGateway
from app.adapters.repositories.postgres.repository import PostgresMessageRepository
from app.adapters.repositories.postgres.sender_repository import PostgresSenderRepository
from app.core.services.message_service import MessageService
from app.core.services.polling_service import PollingOrchestrator
from app.config import config

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

    if config.minio.endpoint:
        container.register(S3Interface, MinioGateway, scope=punq.Scope.singleton)

    container.register(TelegramEngineFactory, instance=TelegramEngineFactory(
        s3=container.resolve(S3Interface) if config.minio.endpoint else None
    ))
    container.register(EmailEngineFactory, instance=EmailEngineFactory())

    container.register(
        DatabaseGateway, PostgresDatabaseGateway, scope=punq.Scope.singleton
    )

    container.register(
        MessageRepository, PostgresMessageRepository, scope=punq.Scope.singleton
    )

    container.register(PollingService, PollingOrchestrator, scope=punq.Scope.singleton)

    container.register(SenderRepository, PostgresSenderRepository, scope=punq.Scope.singleton)

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
