import logging
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database import get_db_session
from src.infrastructure.repository import PostgresMessageRepository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/messages")
async def get_messages(
    channel: Optional[str] = Query(None, description="Фильтр по типу канала"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Получить сообщения с опциональной фильтрацией"""
    repo = PostgresMessageRepository()
    messages = await repo.get_messages(
        channel=channel,
        limit=limit,
        offset=offset
    )
    return [msg.to_dict() for msg in messages]


@router.get("/messages/{message_id}")
async def get_message(
    message_id: str,
):
    """Получить конкретное сообщение по ID"""
    repo = PostgresMessageRepository()
    message = await repo.get_message_by_id(message_id)

    if not message:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Сообщение не найдено")

    return message.to_dict()


@router.post("/messages/reply")
async def reply_to_message(
    message_id: str,
    content: str,
):
    """Ответить на сообщение"""
    repo = PostgresMessageRepository()
    message = await repo.get_message_by_id(message_id)

    if not message:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Сообщение не найдено")

    # TODO: Реализовать логику ответа через соответствующий движок
    logger.info(f"Ответ на {message_id}: {content}")

    return {"status": "success", "message": "Ответ отправлен"}


@router.get("/channels")
async def get_channels():
    """Получить список поддерживаемых каналов"""
    from src.core.models import ChannelType
    return {
        "channels": [
            ChannelType.TELEGRAM,
            ChannelType.EMAIL,
        ]
    }
