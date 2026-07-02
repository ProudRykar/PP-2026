import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.core.domain.models.client import Client, ChannelIdentity
from app.core.ports.client_repository import ClientRepository

logger = logging.getLogger(__name__)


class ClientService:
    def __init__(self, repository: ClientRepository):
        self._repository = repository

    async def get_or_create_client(
        self,
        channel: str,
        external_id: str,
        name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        username: Optional[str] = None,
        display_name: Optional[str] = None,
    ) -> Client:
        client = await self._repository.find_by_channel(channel, external_id)
        if not client and "@" in external_id:
            client = await self._repository.find_by_email(external_id)
        if client:
            changed = False
            if name and name != client.name:
                client.name = name
                changed = True
            if avatar_url and avatar_url != client.avatar_url:
                client.avatar_url = avatar_url
                changed = True

            linked = any(
                ch.channel == channel and ch.external_id == external_id
                for ch in client.channels
            )
            if not linked:
                client.channels.append(
                    ChannelIdentity(
                        channel=channel,
                        external_id=external_id,
                        username=username,
                        display_name=display_name or name,
                    )
                )
                changed = True

            if changed:
                client.last_interaction = datetime.now(timezone.utc)
                await self._repository.update(client)
            else:
                client.last_interaction = datetime.now(timezone.utc)
                await self._repository.update(client)

            return client

        client_id = f"client:{uuid4().hex}"
        now = datetime.now(timezone.utc)
        client = Client(
            id=client_id,
            name=name or external_id,
            avatar_url=avatar_url,
            channels=[
                ChannelIdentity(
                    channel=channel,
                    external_id=external_id,
                    username=username,
                    display_name=display_name or name,
                )
            ],
            created_at=now,
            last_interaction=now,
        )
        await self._repository.save(client)
        logger.info(f"Client created: {client.id} ({name or external_id})")
        return client

    async def add_channel_to_client(
        self,
        client_id: str,
        channel: str,
        external_id: str,
        username: Optional[str] = None,
        display_name: Optional[str] = None,
    ) -> Client:
        client = await self._repository.get_by_id(client_id)
        if not client:
            raise ValueError(f"Client {client_id} not found")

        for ch in client.channels:
            if ch.channel == channel and ch.external_id == external_id:
                return client

        client.channels.append(
            ChannelIdentity(
                channel=channel,
                external_id=external_id,
                username=username,
                display_name=display_name,
            )
        )
        client.last_interaction = datetime.now(timezone.utc)
        await self._repository.update(client)
        return client

    async def get_client(self, client_id: str) -> Optional[Client]:
        return await self._repository.get_by_id(client_id)

    async def update_client(self, client_id: str, updates: dict) -> Client:
        client = await self._repository.get_by_id(client_id)
        if not client:
            raise ValueError(f"Client {client_id} not found")

        for key in ("name", "phone", "email", "avatar_url"):
            if key in updates and updates[key] is not None:
                setattr(client, key, updates[key])
        if "curator_id" in updates:
            client.curator_id = updates["curator_id"] or None
        if "metadata" in updates and updates["metadata"] is not None:
            client.metadata.update(updates["metadata"])

        await self._repository.update(client)
        return client

    async def find_by_channel(self, channel: str, external_id: str) -> Optional[Client]:
        return await self._repository.find_by_channel(channel, external_id)

    async def get_all_clients(self) -> list[Client]:
        return await self._repository.get_all()
