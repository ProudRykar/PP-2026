import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import asyncio
import logging
from dotenv import load_dotenv

from src.api.app import app, websocket_connections
from src.infrastructure.database import init_db, close_db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


async def main():
    """Главная точка входа приложения"""
    logger.info("Начало работы приложения...")
    
    await init_db()
    logger.info("База данных инициализирована")
    
    import uvicorn
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
