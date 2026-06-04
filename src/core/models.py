from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Message:
    """Модель сообщения"""
    id: str
    channel: str
    sender: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]
    recipient: Optional[str] = None
    subject: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь для JSON"""
        return {
            "id": self.id,
            "channel": self.channel,
            "sender": self.sender,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "recipient": self.recipient,
            "subject": self.subject,
        }


class ChannelType:
    """Типы поддерживаемых каналов"""
    TELEGRAM = "telegram"
    EMAIL = "email"
    SLACK = "slack"
    DISCORD = "discord"
    VK = "vk"
