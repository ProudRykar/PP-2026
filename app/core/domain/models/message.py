from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass(slots=True)
class Message:
    id: str
    channel: str
    sender_id: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]
    recipient: Optional[str] = None
    subject: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "channel": self.channel,
            "sender_id": self.sender_id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "recipient": self.recipient,
            "subject": self.subject,
        }
