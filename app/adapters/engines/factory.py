import logging
from typing import Dict

from app.core.ports.engine_factory import EngineFactory
from app.core.ports.message_engine import MessageEngine
from app.core.ports.s3 import S3Interface
from app.adapters.engines.telegram import TelegramEngine
from app.adapters.engines.email import EmailEngine
from app.core.domain.models.channel_type import ChannelType

logger = logging.getLogger(__name__)


class TelegramEngineFactory(EngineFactory):
    def __init__(self, s3: S3Interface | None = None) -> None:
        self._s3 = s3

    def create_engine(self, config: dict) -> MessageEngine:
        token = config.get("token")
        if not token:
            raise ValueError("Telegram token is required")
        return TelegramEngine(token=token, s3=self._s3)

    def get_supported_channel(self) -> str:
        return ChannelType.TELEGRAM


class EmailEngineFactory(EngineFactory):
    def create_engine(self, config: dict) -> MessageEngine:
        required = ["host", "port", "user", "password"]
        for key in required:
            if key not in config:
                raise ValueError(f"Email config missing: {key}")

        return EmailEngine(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            poll_interval=config.get("poll_interval", 60),
            smtp_host=config.get("smtp_host"),
            smtp_port=config.get("smtp_port", 465),
        )

    def get_supported_channel(self) -> str:
        return ChannelType.EMAIL


class EngineAbstractFactory:
    def __init__(self):
        self._factories: Dict[str, EngineFactory] = {}

    def register_factory(self, factory: EngineFactory) -> None:
        channel = factory.get_supported_channel()
        self._factories[channel] = factory
        logger.info(f"Factory registered for channel: {channel}")

    def create_engine(self, channel_type: str, config: dict) -> MessageEngine:
        if channel_type not in self._factories:
            raise ValueError(f"No factory registered for channel: {channel_type}")

        engine = self._factories[channel_type].create_engine(config)
        logger.info(f"Created engine {channel_type}")
        return engine

    def get_supported_channels(self) -> list:
        return list(self._factories.keys())
