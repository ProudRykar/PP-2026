from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from app.core.domain.models.channel_type import CuratorRole, CuratorStatus


@dataclass(slots=True)
class Curator:
    id: str
    full_name: str
    login: str
    email: str
    role: CuratorRole = CuratorRole.AGENT
    status: CuratorStatus = CuratorStatus.ACTIVE
    avatar_url: Optional[str] = None
    password_hash: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "login": self.login,
            "email": self.email,
            "role": self.role.value,
            "status": self.status.value,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat()
            if self.last_activity
            else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Curator":
        return Curator(
            id=data["id"],
            full_name=data["full_name"],
            login=data["login"],
            email=data["email"],
            role=CuratorRole(data.get("role", CuratorRole.AGENT.value)),
            status=CuratorStatus(data.get("status", CuratorStatus.ACTIVE.value)),
            avatar_url=data.get("avatar_url"),
            password_hash=data.get("password_hash"),
            created_at=data.get("created_at", datetime.now(timezone.utc)),
            last_activity=data.get("last_activity"),
        )


@dataclass(slots=True)
class AssignmentHistory:
    id: str
    message_id: str
    from_curator_id: Optional[str] = None
    to_curator_id: Optional[str] = None
    assigned_by: Optional[str] = None
    reason: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "message_id": self.message_id,
            "from_curator_id": self.from_curator_id,
            "to_curator_id": self.to_curator_id,
            "assigned_by": self.assigned_by,
            "reason": self.reason,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }
