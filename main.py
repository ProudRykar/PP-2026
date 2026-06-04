import asyncio
import logging
import os
from dotenv import load_dotenv

from src.infrastructure.di_container import configure_container, initialize_factories
from src.engines.factory import EngineAbstractFactory
from src.services.polling_service import PollingService
from src.api.app import app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


def create_engines_from_env(container, abstract_factory: EngineAbstractFactory):
    """Создать движки на основе переменных окружения и зарегистрировать их в абстрактной фабрике"""
    engines = []

    # Telegram
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if tg_token and tg_token != "your_telegram_bot_token_here":
        try:
            engine = abstract_factory.create_engine("telegram", {"token": tg_token})
            engines.append(engine)
            logger.info("Движок Telegram создан")
        except Exception as e:
            logger.error(f"Не удалось создать движок Telegram: {e}")

    # Email
    email_host = os.getenv("EMAIL_HOST")
    if email_host:
        try:
            engine = abstract_factory.create_engine("email", {
                "host": email_host,
                "port": int(os.getenv("EMAIL_PORT", 993)),
                "user": os.getenv("EMAIL_USER"),
                "password": os.getenv("EMAIL_PASSWORD"),
                "poll_interval": int(os.getenv("EMAIL_POLL_INTERVAL", 60))
            })
            engines.append(engine)
            logger.info("Движок Email создан")
        except Exception as e:
            logger.error(f"Не удалось создать движок Email: {e}")

    return engines


async def main():
    """Основная точка входа"""
    logger.info("Запуск решения для омниканального обмена сообщениями...")

    container = configure_container()
    initialize_factories(container)

    abstract_factory = container.resolve(EngineAbstractFactory)
    engines = create_engines_from_env(container, abstract_factory)

    if not engines:
        logger.warning("Движки не сконфигурированы")

    polling_service = container.resolve(PollingService)
    for engine in engines:
        polling_service.register_engine(engine)

    await polling_service.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
