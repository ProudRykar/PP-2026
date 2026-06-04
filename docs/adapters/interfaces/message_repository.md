## Класс MessageRepository


```python
class MessageRepository(ABC):
```

---
## def save_message:

```python
    @abstractmethod
    async def save_message(self, message: Message) -> None:
        pass
```
---
## def get_messages:

```python
    @abstractmethod
    async def get_messages(
        self, channel: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[Message]:
        pass
```
---
## def get_message_by_id:

```python
    @abstractmethod
    async def get_message_by_id(self, message_id: str) -> Optional[Message]:
        pass
```
---