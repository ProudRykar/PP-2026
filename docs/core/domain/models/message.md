## Класс Message


```python
@dataclass
class Message:
    id: str
    channel: str
    sender: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]
    recipient: Optional[str] = None
    subject: Optional[str] = None
```

---
## def to_dict:

```python
    def to_dict(self) -> Dict[str, Any]:
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
```
---