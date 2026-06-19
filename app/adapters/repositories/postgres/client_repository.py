import logging
from typing import Optional, List, cast
from datetime import datetime

from sqlalchemy import select, desc, delete

from app.core.ports.client_repository import ClientRepository
from app.core.domain.models.client import Client, ChannelIdentity
from app.core.ports.db import DatabaseGateway
from app.adapters.repositories.postgres.client_models import (
    ClientModel,
    ClientChannelModel,
)

logger = logging.getLogger(__name__)


class PostgresClientRepository(ClientRepository):
    def __init__(self, db: DatabaseGateway):
        self._db = db

    async def save(self, client: Client) -> None:
        async with self._db.get_session() as session:
            model = ClientModel(
                id=client.id,
                name=client.name,
                phone=client.phone,
                email=client.email,
                avatar_url=client.avatar_url,
                metadata_=client.metadata or {},
                created_at=client.created_at,
                last_interaction=client.last_interaction,
            )
            session.add(model)
            await session.flush()
            for ch in client.channels:
                ch_model = ClientChannelModel(
                    id=f"{client.id}:{ch.channel}:{ch.external_id}",
                    client_id=client.id,
                    channel=str(ch.channel),
                    external_id=str(ch.external_id),
                    username=ch.username,
                    display_name=ch.display_name,
                )
                session.add(ch_model)
            logger.debug(f"Client saved: {client.id}")

    async def get_by_id(self, client_id: str) -> Optional[Client]:
        async with self._db.get_session() as session:
            result = await session.execute(
                select(ClientModel).where(ClientModel.id == client_id)
            )
            model = result.scalar_one_or_none()
            if not model:
                return None
            channels = await self._get_channels(session, client_id)
            return self._to_client(model, channels)

    async def find_by_channel(self, channel: str, external_id: str) -> Optional[Client]:
        async with self._db.get_session() as session:
            result = await session.execute(
                select(ClientChannelModel).where(
                    ClientChannelModel.channel == channel,
                    ClientChannelModel.external_id == external_id,
                )
            )
            ch_model = result.scalar_one_or_none()
            if not ch_model:
                return None
            return await self.get_by_id(cast(str, ch_model.client_id))

    async def find_by_email(self, email: str) -> Optional[Client]:
        async with self._db.get_session() as session:
            result = await session.execute(
                select(ClientModel).where(ClientModel.email == email)
            )
            model = result.scalar_one_or_none()
            if not model:
                return None
            channels = await self._get_channels(session, cast(str, model.id))
            return self._to_client(model, channels)

    async def update(self, client: Client) -> None:
        async with self._db.get_session() as session:
            result = await session.execute(
                select(ClientModel).where(ClientModel.id == client.id)
            )
            model = result.scalar_one_or_none()
            if not model:
                raise ValueError(f"Client {client.id} not found")
            model.name = client.name  # type: ignore[assignment]
            model.phone = client.phone  # type: ignore[assignment]
            model.email = client.email  # type: ignore[assignment]
            model.avatar_url = client.avatar_url  # type: ignore[assignment]
            model.metadata_ = client.metadata or {}  # type: ignore[assignment]
            model.last_interaction = client.last_interaction  # type: ignore[assignment]

            await session.execute(
                delete(ClientChannelModel).where(
                    ClientChannelModel.client_id == client.id
                )
            )
            for ch in client.channels:
                ch_model = ClientChannelModel(
                    id=f"{client.id}:{ch.channel}:{ch.external_id}",
                    client_id=client.id,
                    channel=str(ch.channel),
                    external_id=str(ch.external_id),
                    username=ch.username,
                    display_name=ch.display_name,
                )
                session.add(ch_model)
            logger.debug(f"Client updated: {client.id}")

    async def get_all(self) -> List[Client]:
        async with self._db.get_session() as session:
            result = await session.execute(
                select(ClientModel).order_by(desc(ClientModel.last_interaction))
            )
            models = result.scalars().all()
            clients: List[Client] = []
            for m in models:
                channels = await self._get_channels(session, cast(str, m.id))
                clients.append(self._to_client(m, channels))
            return clients

    async def _get_channels(self, session, client_id: str) -> List[ClientChannelModel]:
        result = await session.execute(
            select(ClientChannelModel).where(ClientChannelModel.client_id == client_id)
        )
        return list(result.scalars().all())

    def _to_client(self, m: ClientModel, channels: List[ClientChannelModel]) -> Client:
        return Client(
            id=cast(str, m.id),
            name=cast(str, m.name),
            phone=cast(Optional[str], m.phone),
            email=cast(Optional[str], m.email),
            avatar_url=cast(Optional[str], m.avatar_url),
            channels=[
                ChannelIdentity(
                    channel=cast(str, ch.channel),
                    external_id=cast(str, ch.external_id),
                    username=cast(Optional[str], ch.username),
                    display_name=cast(Optional[str], ch.display_name),
                )
                for ch in channels
            ],
            metadata=cast(dict, m.metadata_ if m.metadata_ else {}),
            created_at=cast(datetime, m.created_at),
            last_interaction=cast(Optional[datetime], m.last_interaction),
        )
