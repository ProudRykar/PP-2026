from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any


@dataclass(slots=True)
class ChannelIdentityResponse:
    channel: str
    external_id: str
    username: Optional[str] = None
    display_name: Optional[str] = None


@dataclass(slots=True)
class ClientResponse:
    id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    channels: list[ChannelIdentityResponse] | None = None
    metadata: dict[str, Any] | None = None
    created_at: Optional[datetime] = None
    last_interaction: Optional[datetime] = None


@dataclass(slots=True)
class ClientUpdateRequest:
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
