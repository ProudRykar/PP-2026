from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

from app.core.domain.models.channel_type import MessageType


@dataclass(slots=True)
class Message:
    id: str
    channel: str
    sender_id: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]
    message_type: MessageType = MessageType.TEXT
    recipient: Optional[str] = None
    subject: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "channel": self.channel,
            "sender_id": self.sender_id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "message_type": self.message_type.value,
            "metadata": self.metadata,
            "recipient": self.recipient,
            "subject": self.subject,
        }
