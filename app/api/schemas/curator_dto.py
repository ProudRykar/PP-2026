from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass(slots=True)
class CuratorResponse:
    id: str
    full_name: str
    login: str
    email: str
    role: str = "agent"
    status: str = "active"
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None


@dataclass(slots=True)
class CuratorCreateRequest:
    full_name: str
    login: str
    email: str
    role: str = "agent"
    avatar_url: Optional[str] = None


@dataclass(slots=True)
class CuratorUpdateRequest:
    full_name: Optional[str] = None
    login: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    avatar_url: Optional[str] = None


@dataclass(slots=True)
class AssignCuratorRequest:
    curator_id: str
    reason: Optional[str] = None


@dataclass(slots=True)
class TransferRequest:
    from_curator_id: str
    to_curator_id: str
    reason: Optional[str] = None


@dataclass(slots=True)
class AssignmentHistoryResponse:
    id: str
    message_id: str
    from_curator_id: Optional[str] = None
    to_curator_id: Optional[str] = None
    assigned_by: Optional[str] = None
    reason: Optional[str] = None
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
