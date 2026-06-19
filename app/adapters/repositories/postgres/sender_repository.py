import logging
from typing import Optional, cast

from sqlalchemy import select

from app.core.ports.sender_repository import SenderRepository
from app.core.domain.models.sender import Sender
from app.core.ports.db import DatabaseGateway
from app.adapters.repositories.postgres.models import SenderModel

logger = logging.getLogger(__name__)


class PostgresSenderRepository(SenderRepository):
    def __init__(self, db: DatabaseGateway):
        self._db = db

    async def save(self, sender: Sender) -> None:
        async with self._db.get_session() as session:
            model = SenderModel(
                id=sender.id,
                name=sender.id,
            )
            await session.merge(model)
            logger.debug(f"Sender saved: {sender.id}")

    async def get_by_id(self, sender_id: str) -> Optional[Sender]:
        async with self._db.get_session() as session:
            result = await session.execute(
                select(SenderModel).where(SenderModel.id == sender_id)
            )
            model = result.scalar_one_or_none()
            if model:
                return Sender(id=cast(str, model.id), apps={})
            return None

    async def find_by_identity(self, channel: str, address: str) -> Optional[Sender]:
        return None

    async def find_all(self) -> list[Sender]:
        async with self._db.get_session() as session:
            result = await session.execute(select(SenderModel))
            return [Sender(id=cast(str, m.id), apps={}) for m in result.scalars().all()]
