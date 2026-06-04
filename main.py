import asyncio
import logging
import os
from dotenv import load_dotenv

from app.container import configure_container, initialize_factories
from app.adapters.engines.factory import EngineAbstractFactory
from app.adapters.interfaces.db import DatabaseGateway
from app.adapters.interfaces.polling_service import PollingService

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()


def create_engines_from_env(container, abstract_factory: EngineAbstractFactory):
    engines = []

    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if tg_token and tg_token != "your_telegram_bot_token_here":
        try:
            engine = abstract_factory.create_engine("telegram", {"token": tg_token})
            engines.append(engine)
            logger.info("Telegram engine created")
        except Exception as e:
            logger.error(f"Failed to create Telegram engine: {e}")

    email_host = os.getenv("EMAIL_HOST")
    if email_host:
        try:
            engine = abstract_factory.create_engine(
                "email",
                {
                    "host": email_host,
                    "port": int(os.getenv("EMAIL_PORT", 993)),
                    "user": os.getenv("EMAIL_USER"),
                    "password": os.getenv("EMAIL_PASSWORD"),
                    "poll_interval": int(os.getenv("EMAIL_POLL_INTERVAL", 60)),
                },
            )
            engines.append(engine)
            logger.info("Email engine created")
        except Exception as e:
            logger.error(f"Failed to create Email engine: {e}")

    return engines


async def main():
    logger.info("Starting omnichannel messaging solution...")

    container = configure_container()
    initialize_factories(container)

    db = container.resolve(DatabaseGateway)
    await db.init()

    abstract_factory = container.resolve(EngineAbstractFactory)
    engines = create_engines_from_env(container, abstract_factory)

    if not engines:
        logger.warning("No engines configured")

    polling_service = container.resolve(PollingService)
    for engine in engines:
        polling_service.register_engine(engine)

    await polling_service.start_polling()

    await db.close()


if __name__ == "__main__":
    asyncio.run(main())
