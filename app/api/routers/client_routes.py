import dataclasses
import logging

from litestar import Controller, get, put
from litestar.params import Parameter

from app.api.schemas.client_dto import (
    ClientResponse,
    ClientUpdateRequest,
    ChannelIdentityResponse,
)
from app.core.services.client_service import ClientService

logger = logging.getLogger(__name__)


def _to_response(client) -> ClientResponse:
    return ClientResponse(
        id=client.id,
        name=client.name,
        phone=client.phone,
        email=client.email,
        avatar_url=client.avatar_url,
        channels=[
            ChannelIdentityResponse(
                channel=ch.channel,
                external_id=ch.external_id,
                username=ch.username,
                display_name=ch.display_name,
            )
            for ch in (client.channels or [])
        ],
        metadata=client.metadata,
        created_at=client.created_at,
        last_interaction=client.last_interaction,
    )


class ClientController(Controller):
    path = "/api/clients"

    @get()
    async def list_clients(
        self,
        client_service: ClientService,
    ) -> list[ClientResponse]:
        clients = await client_service.get_all_clients()
        return [_to_response(c) for c in clients]

    @get("/{client_id:str}")
    async def get_client(
        self,
        client_id: str,
        client_service: ClientService,
    ) -> ClientResponse:
        client = await client_service.get_client(client_id)
        if not client:
            from litestar.exceptions import HTTPException

            raise HTTPException(status_code=404, detail=f"Client {client_id} not found")
        return _to_response(client)

    @put("/{client_id:str}")
    async def update_client(
        self,
        client_id: str,
        data: ClientUpdateRequest,
        client_service: ClientService,
    ) -> ClientResponse:
        updates = {
            f.name: getattr(data, f.name)
            for f in dataclasses.fields(data)
            if getattr(data, f.name) is not None
        }
        client = await client_service.update_client(client_id, updates)
        return _to_response(client)

    @get("/by-channel")
    async def find_client_by_channel(
        self,
        client_service: ClientService,
        channel: str = Parameter(description="Channel type"),
        external_id: str = Parameter(description="External ID on that channel"),
    ) -> ClientResponse | None:
        client = await client_service.find_by_channel(channel, external_id)
        if not client:
            return None
        return _to_response(client)
