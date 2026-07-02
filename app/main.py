import logging
import asyncio
import os
from contextlib import asynccontextmanager

from litestar import Litestar, WebSocket, websocket
from litestar.di import Provide
from litestar.static_files import create_static_files_router

from app.api.dependencies import (
    get_message_service,
    get_polling_service,
    get_client_service,
    get_curator_service,
    get_auth_service,
)
from app.api.exceptions.handlers import EXCEPTION_HANDLERS
from app.api.routers.routes import MessageController
from app.api.routers.health import HealthController
from app.api.routers.client_routes import ClientController
from app.api.routers.curator_routes import CuratorController, AssignmentController
from app.api.routers.auth_routes import AuthController
from app.adapters.engines.factory import EngineAbstractFactory
from app.core.ports.db import DatabaseGateway
from app.core.ports.polling_service import PollingService
from app.config import config
from app.container import get_container, initialize_factories
from app.events import websocket_connections

logger = logging.getLogger(__name__)


def create_engines_from_env(abstract_factory: EngineAbstractFactory):
    engines = []

    if config.telegram.token:
        try:
            engine = abstract_factory.create_engine(
                "telegram", {"token": config.telegram.token}
            )
            engines.append(engine)
            logger.info("Telegram engine created")
        except Exception as e:
            logger.error(f"Error creating Telegram engine: {e}")

    if config.email.host:
        try:
            engine = abstract_factory.create_engine(
                "email",
                {
                    "host": config.email.host,
                    "port": config.email.port,
                    "user": config.email.user,
                    "password": config.email.password,
                    "poll_interval": config.email.poll_interval,
                    "smtp_host": config.email.smtp_host,
                    "smtp_port": config.email.smtp_port,
                },
            )
            engines.append(engine)
            logger.info("Email engine created")
        except Exception as e:
            logger.error(f"Error creating Email engine: {e}")

    return engines


@asynccontextmanager
async def lifespan(app: Litestar):
    logger.info("Starting application...")

    container = get_container()

    db = container.resolve(DatabaseGateway)
    await db.init()
    logger.info("Database initialized")

    abstract_factory = initialize_factories(container)

    engines = create_engines_from_env(abstract_factory)

    if engines:
        polling_service = container.resolve(PollingService)
        for engine in engines:
            try:
                polling_service.register_engine(engine)
            except Exception as e:
                logger.error(f"Error registering engine: {e}")

        asyncio.create_task(polling_service.start_polling())
        logger.info(f"Polling started for {len(engines)} engines")
    else:
        logger.warning("No engines configured! Check .env file")

    yield

    logger.info("Shutting down...")
    if engines:
        polling_service = container.resolve(PollingService)
        await polling_service.stop_polling()
    await db.close()
    logger.info("Application shut down")


@websocket("/ws")
async def websocket_handler(socket: WebSocket) -> None:
    await socket.accept()
    websocket_connections.append(socket)
    try:
        while True:
            await socket.receive_text()
    except Exception:
        try:
            websocket_connections.remove(socket)
        except ValueError:
            pass


route_handlers: list = [
    MessageController,
    HealthController,
    ClientController,
    CuratorController,
    AssignmentController,
    AuthController,
    websocket_handler,
]

if os.path.exists("frontend/dist"):
    route_handlers.append(
        create_static_files_router(path="/", directories=["frontend/dist"], html_mode=True)
    )
elif os.path.exists("frontend"):
    route_handlers.append(
        create_static_files_router(path="/", directories=["frontend"], html_mode=True)
    )


app = Litestar(
    route_handlers=route_handlers,
    lifespan=[lifespan],
    dependencies={
        "service": Provide(get_message_service, sync_to_thread=False),
        "polling": Provide(get_polling_service, sync_to_thread=False),
        "client_service": Provide(get_client_service, sync_to_thread=False),
        "curator_service": Provide(get_curator_service, sync_to_thread=False),
        "auth_service": Provide(get_auth_service, sync_to_thread=False),
    },
    exception_handlers=EXCEPTION_HANDLERS,  # type: ignore[arg-type]
)
