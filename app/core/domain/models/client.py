from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List


@dataclass(slots=True)
class ChannelIdentity:
    channel: str
    external_id: str
    username: Optional[str] = None
    display_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "channel": self.channel,
            "external_id": self.external_id,
        }
        if self.username is not None:
            d["username"] = self.username
        if self.display_name is not None:
            d["display_name"] = self.display_name
        return d


@dataclass(slots=True)
class Client:
    id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    channels: List[ChannelIdentity] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_interaction: Optional[datetime] = None
    curator_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "avatar_url": self.avatar_url,
            "channels": [ch.to_dict() for ch in self.channels],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_interaction": self.last_interaction.isoformat()
            if self.last_interaction
            else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Client":
        channels = [
            ChannelIdentity(
                channel=ch["channel"],
                external_id=ch["external_id"],
                username=ch.get("username"),
                display_name=ch.get("display_name"),
            )
            for ch in data.get("channels", [])
        ]
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        last_interaction = data.get("last_interaction")
        if isinstance(last_interaction, str):
            last_interaction = datetime.fromisoformat(last_interaction)
        return Client(
            id=data["id"],
            name=data["name"],
            phone=data.get("phone"),
            email=data.get("email"),
            avatar_url=data.get("avatar_url"),
            channels=channels,
            metadata=data.get("metadata", {}),
            created_at=created_at or datetime.now(timezone.utc),
            last_interaction=last_interaction,
        )
