from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass(slots=True)
class MessageResponse:
    id: str
    channel: str
    sender: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]
    recipient: Optional[str] = None
    subject: Optional[str] = None


@dataclass(slots=True)
class ReplyRequest:
    message_id: str
    content: str
