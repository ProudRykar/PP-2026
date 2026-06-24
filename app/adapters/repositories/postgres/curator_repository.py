import logging
from typing import Optional, List, Dict, Any, cast
from datetime import datetime

from sqlalchemy import select, desc

from app.core.ports.curator_repository import (
    CuratorRepository,
    AssignmentHistoryRepository,
)
from app.core.domain.models.curator import Curator, AssignmentHistory
from app.core.domain.models.channel_type import CuratorRole, CuratorStatus
from app.core.ports.db import DatabaseGateway
from app.adapters.repositories.postgres.curator_models import (
    CuratorModel,
    AssignmentHistoryModel,
)
from app.core.errors.curator import CuratorNotFoundError

logger = logging.getLogger(__name__)


class PostgresCuratorRepository(CuratorRepository):
    def __init__(self, db: DatabaseGateway):
        self._db = db

    async def save(self, curator: Curator) -> None:
        async with self._db.get_session() as session:
            model = CuratorModel(
                id=curator.id,
                full_name=curator.full_name,
                login=curator.login,
                email=curator.email,
                role=curator.role.value,
                status=curator.status.value,
                avatar_url=curator.avatar_url,
                password_hash=curator.password_hash,
                created_at=curator.created_at,
                last_activity=curator.last_activity,
            )
            session.add(model)
            logger.debug(f"Curator saved: {curator.id}")

    async def get_by_id(self, curator_id: str) -> Optional[Curator]:
        async with self._db.get_session() as session:
            result = await session.execute(
                select(CuratorModel).where(CuratorModel.id == curator_id)
            )
            model = result.scalar_one_or_none()
            return self._to_curator(model) if model else None

    async def get_by_login(self, login: str) -> Optional[Curator]:
        async with self._db.get_session() as session:
            result = await session.execute(
                select(CuratorModel).where(CuratorModel.login == login)
            )
            model = result.scalar_one_or_none()
            return self._to_curator(model) if model else None

    async def get_all(self, status: Optional[str] = None) -> List[Curator]:
        async with self._db.get_session() as session:
            query = select(CuratorModel).order_by(CuratorModel.created_at)
            if status:
                query = query.where(CuratorModel.status == status)
            result = await session.execute(query)
            models = result.scalars().all()
            return [self._to_curator(m) for m in models]

    async def update(self, curator: Curator) -> None:
        async with self._db.get_session() as session:
            result = await session.execute(
                select(CuratorModel).where(CuratorModel.id == curator.id)
            )
            model = result.scalar_one_or_none()
            if not model:
                raise CuratorNotFoundError(curator.id)

            model.full_name = curator.full_name
            model.login = curator.login
            model.email = curator.email
            model.role = curator.role.value
            model.status = curator.status.value
            model.avatar_url = curator.avatar_url
            model.password_hash = curator.password_hash
            model.last_activity = curator.last_activity
            logger.debug(f"Curator updated: {curator.id}")

    async def delete(self, curator_id: str) -> None:
        async with self._db.get_session() as session:
            result = await session.execute(
                select(CuratorModel).where(CuratorModel.id == curator_id)
            )
            model = result.scalar_one_or_none()
            if not model:
                raise CuratorNotFoundError(curator_id)
            await session.delete(model)
            logger.debug(f"Curator deleted: {curator_id}")

    def _to_curator(self, m: CuratorModel) -> Curator:
        return Curator(
            id=cast(str, m.id),
            full_name=cast(str, m.full_name),
            login=cast(str, m.login),
            email=cast(str, m.email),
            role=CuratorRole(cast(str, m.role)) if m.role else CuratorRole.AGENT,
            status=CuratorStatus(cast(str, m.status))
            if m.status
            else CuratorStatus.ACTIVE,
            avatar_url=cast(Optional[str], m.avatar_url),
            password_hash=cast(Optional[str], m.password_hash),
            created_at=cast(datetime, m.created_at),
            last_activity=cast(Optional[datetime], m.last_activity),
        )


class PostgresAssignmentHistoryRepository(AssignmentHistoryRepository):
    def __init__(self, db: DatabaseGateway):
        self._db = db

    async def save(self, entry: AssignmentHistory) -> None:
        async with self._db.get_session() as session:
            model = AssignmentHistoryModel(
                id=entry.id,
                message_id=entry.message_id,
                from_curator_id=entry.from_curator_id,
                to_curator_id=entry.to_curator_id,
                assigned_by=entry.assigned_by,
                reason=entry.reason,
                created_at=entry.created_at,
                metadata_=entry.metadata,
            )
            session.add(model)
            logger.debug(f"Assignment history saved: {entry.id}")

    async def get_by_message(self, message_id: str) -> List[AssignmentHistory]:
        async with self._db.get_session() as session:
            result = await session.execute(
                select(AssignmentHistoryModel)
                .where(AssignmentHistoryModel.message_id == message_id)
                .order_by(desc(AssignmentHistoryModel.created_at))
            )
            models = result.scalars().all()
            return [self._to_entry(m) for m in models]

    async def get_by_curator(self, curator_id: str) -> List[AssignmentHistory]:
        async with self._db.get_session() as session:
            result = await session.execute(
                select(AssignmentHistoryModel)
                .where(
                    (AssignmentHistoryModel.to_curator_id == curator_id)
                    | (AssignmentHistoryModel.from_curator_id == curator_id)
                )
                .order_by(desc(AssignmentHistoryModel.created_at))
            )
            models = result.scalars().all()
            return [self._to_entry(m) for m in models]

    async def get_current_assignment(
        self, message_id: str
    ) -> Optional[AssignmentHistory]:
        async with self._db.get_session() as session:
            result = await session.execute(
                select(AssignmentHistoryModel)
                .where(AssignmentHistoryModel.message_id == message_id)
                .order_by(desc(AssignmentHistoryModel.created_at))
                .limit(1)
            )
            model = result.scalar_one_or_none()
            return self._to_entry(model) if model else None

    def _to_entry(self, m: AssignmentHistoryModel) -> AssignmentHistory:
        return AssignmentHistory(
            id=cast(str, m.id),
            message_id=cast(str, m.message_id),
            from_curator_id=cast(Optional[str], m.from_curator_id),
            to_curator_id=cast(Optional[str], m.to_curator_id),
            assigned_by=cast(Optional[str], m.assigned_by),
            reason=cast(Optional[str], m.reason),
            created_at=cast(datetime, m.created_at),
            metadata=cast(Dict[str, Any], m.metadata_ if m.metadata_ else {}),
        )
