from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass(slots=True)
class MessageResponse:
    id: str
    channel: str
    sender_id: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]
    recipient: Optional[str] = None
    subject: Optional[str] = None
    message_type: str = "text"
    parent_id: Optional[str] = None
    curator_id: Optional[str] = None


@dataclass(slots=True)
class ReplyRequest:
    message_id: str
    content: str
    subject: Optional[str] = None
    file_url: Optional[str] = None
