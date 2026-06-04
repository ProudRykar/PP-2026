import logging
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()  # Загрузить переменные из .env файла

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.api.routes import router as api_router
from src.infrastructure.di_container import get_container, initialize_factories
from src.infrastructure.database import init_db, close_db
from src.infrastructure.repository import PostgresMessageRepository
from src.engines.factory import EngineAbstractFactory
from src.services.polling_service import PollingService
import os

logger = logging.getLogger(__name__)

# WebSocket соединения для обновлений в реальном времени
websocket_connections: list[WebSocket] = []


def create_engines_from_env(abstract_factory: EngineAbstractFactory, repository=None):
    """Создать экземпляры движков из переменных окружения"""
    engines = []

    # Telegram
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if tg_token and tg_token != "your_telegram_bot_token_here":
        try:
            engine = abstract_factory.create_engine("telegram", {"token": tg_token}, repository=repository)
            engines.append(engine)
            logger.info("Движок Telegram создан")
        except Exception as e:
            logger.error(f"Ошибка создания движка Telegram: {e}")

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
            }, repository=repository)
            engines.append(engine)
            logger.info("Движок Email создан")
        except Exception as e:
            logger.error(f"Ошибка создания движка Email: {e}")

    return engines


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения"""
    # Запуск
    logger.info("Запуск приложения...")

    # Инициализация базы данных
    await init_db()
    logger.info("База данных инициализирована")

    # Настройка DI контейнера
    container = get_container()
    abstract_factory = initialize_factories(container)

    # Создание репозитория
    repository = PostgresMessageRepository()

    # Создание движков из переменных окружения и настройка опроса
    engines = create_engines_from_env(abstract_factory, repository)

    if engines:
        polling_service = container.resolve(PollingService)
        for engine in engines:
            try:
                polling_service.register_engine(engine)
            except Exception as e:
                logger.error(f"Ошибка регистрации движка: {e}")

        # Запуск опроса в фоновой задаче
        asyncio.create_task(polling_service.start_polling())
        logger.info(f"Опрос запущен для {len(engines)} движков")
    else:
        logger.warning("Ни один движок не настроен! Проверьте файл .env")

    yield

    # Завершение работы
    logger.info("Завершение работы...")
    if engines:
        polling_service = container.resolve(PollingService)
        await polling_service.stop_polling()
    await close_db()
    logger.info("Приложение завершило работу")


app = FastAPI(
    title="Омниканальное решение для сообщений",
    description="Унифицированное решение для нескольких каналов",
    version="1.0.0",
    lifespan=lifespan
)

# Подключение маршрутов API
app.include_router(api_router, prefix="/api")


# WebSocket эндпоинт для обновлений в реальном времени
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)


# Монтирование статических файлов для фронтенда
if os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


@app.get("/health")
async def health_check():
    """Эндпоинт проверки работоспособности"""
    return {"status": "healthy", "service": "omnichannel"}


async def broadcast_message(message: dict):
    """Трансляция нового сообщения всем WebSocket соединениям"""
    for connection in websocket_connections:
        try:
            await connection.send_json(message)
        except:
            pass
