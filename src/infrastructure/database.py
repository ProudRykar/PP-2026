import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from typing import Optional

load_dotenv()  # Загрузить файл .env

Base = declarative_base()

_database_url: Optional[str] = None
_engine = None
_async_session = None


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")

    if not url:
        raise ValueError("DATABASE_URL is not set")

    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    return url


def get_engine():
    """Ленивая загрузка движка базы данных"""
    global _engine
    if _engine is None:
        url = get_database_url()
        _engine = create_async_engine(
            url,
            echo=os.getenv("DEBUG", "false").lower() == "true",
            pool_size=10,
            max_overflow=20,
            poolclass=NullPool if os.getenv("TESTING") else None,
        )
    return _engine


def get_async_sessionmaker():
    """Ленивая загрузка фабрики сессий"""
    global _async_session
    if _async_session is None:
        _async_session = async_sessionmaker(
            get_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _async_session


async def get_db_session() -> AsyncSession:
    """Зависимость для получения сессии БД"""
    async_session = get_async_sessionmaker()
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """Инициализировать базу данных (создать таблицы)"""
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Закрыть соединения с базой данных"""
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None
