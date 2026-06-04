## Класс MessageResponse


```python
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
```
## Класс ReplyRequest


```python
@dataclass(slots=True)
class ReplyRequest:
    message_id: str
    content: str
```