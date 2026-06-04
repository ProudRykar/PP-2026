import logging
from typing import Dict
from src.core.interfaces import EngineFactory, MessageEngine
from src.engines.telegram import TelegramEngine
from src.engines.email import EmailEngine
from src.core.models import ChannelType
from src.infrastructure.repository import PostgresMessageRepository

logger = logging.getLogger(__name__)


class TelegramEngineFactory(EngineFactory):
    """Фабрика для создания движков Telegram"""

    def create_engine(self, config: dict, repository=None) -> MessageEngine:
        token = config.get('token')
        if not token:
            raise ValueError("Требуется токен Telegram")
        return TelegramEngine(token=token, repository=repository)

    def get_supported_channel(self) -> str:
        return ChannelType.TELEGRAM


class EmailEngineFactory(EngineFactory):
    """Фабрика для создания движков Email"""

    def create_engine(self, config: dict, repository=None) -> MessageEngine:
        required = ['host', 'port', 'user', 'password']
        for key in required:
            if key not in config:
                raise ValueError(f"В конфигурации Email отсутствует параметр: {key}")

        return EmailEngine(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            poll_interval=config.get('poll_interval', 60),
            repository=repository
        )

    def get_supported_channel(self) -> str:
        return ChannelType.EMAIL


class EngineAbstractFactory:
    """Главная абстрактная фабрика, управляющая всеми фабриками движков"""

    def __init__(self):
        self._factories: Dict[str, EngineFactory] = {}

    def register_factory(self, factory: EngineFactory) -> None:
        """Зарегистрировать фабрику движков"""
        channel = factory.get_supported_channel()
        self._factories[channel] = factory
        logger.info(f"Зарегистрирована фабрика для канала: {channel}")

    def create_engine(self, channel_type: str, config: dict, repository=None) -> MessageEngine:
        """Создать движок, используя соответствующую фабрику"""
        if channel_type not in self._factories:
            raise ValueError(f"Нет зарегистрированной фабрики для канала: {channel_type}")

        engine = self._factories[channel_type].create_engine(config, repository)
        logger.info(f"Создан движок {channel_type}")
        return engine

    def get_supported_channels(self) -> list:
        """Вернуть список поддерживаемых типов каналов"""
        return list(self._factories.keys())
