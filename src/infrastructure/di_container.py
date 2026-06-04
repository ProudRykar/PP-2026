import logging
import punq
from src.engines.factory import (
    EngineAbstractFactory,
    TelegramEngineFactory,
    EmailEngineFactory,
)
from src.core.interfaces import MessageRepository
from src.infrastructure.repository import PostgresMessageRepository
from src.services.message_service import MessageService
from src.services.polling_service import PollingService

logger = logging.getLogger(__name__)

# Глобальный экземпляр контейнера
_container: punq.Container = None


def get_container() -> punq.Container:
    """Получить или создать глобальный DI контейнер"""
    global _container
    if _container is None:
        _container = configure_container()
    return _container


def configure_container() -> punq.Container:
    """
    Настроить DI контейнер punq со всеми зависимостями
    """
    container = punq.Container()

    # Регистрация абстрактной фабрики как синглтона
    container.register(EngineAbstractFactory, scope=punq.Scope.singleton)

    # Регистрация конкретных фабрик
    container.register(TelegramEngineFactory, instance=TelegramEngineFactory())
    container.register(EmailEngineFactory, instance=EmailEngineFactory())

    # Регистрация репозитория как реализации интерфейса MessageRepository
    container.register(MessageRepository, PostgresMessageRepository, scope=punq.Scope.singleton)

    # Регистрация сервисов
    container.register(MessageService)
    container.register(PollingService)

    logger.info("DI контейнер настроен")
    return container


def initialize_factories(container: punq.Container) -> EngineAbstractFactory:
    """
    Инициализировать абстрактную фабрику всеми зарегистрированными конкретными фабриками.
    Должно вызываться после настройки контейнера.
    """
    abstract_factory = container.resolve(EngineAbstractFactory)

    # Регистрация каждой конкретной фабрики в абстрактной фабрике
    telegram_factory = container.resolve(TelegramEngineFactory)
    abstract_factory.register_factory(telegram_factory)

    email_factory = container.resolve(EmailEngineFactory)
    abstract_factory.register_factory(email_factory)

    logger.info("Все фабрики движков инициализированы")
    return abstract_factory
