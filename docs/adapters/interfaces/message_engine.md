## Класс MessageEngine


```python
class MessageEngine(ABC):
```

---
## def start:

```python
    @abstractmethod
    async def start(self) -> None:
        pass
```
---
## def stop:

```python
    @abstractmethod
    async def stop(self) -> None:
        pass
```
---
## def send_message:

```python
    @abstractmethod
    async def send_message(self, recipient: str, content: str, **kwargs) -> str:
        pass
```
---
## def get_incoming:

```python
    @abstractmethod
    def get_incoming(self) -> AsyncIterator[Message]:
        pass
```
---
## def channel_type:

```python
    @property
    @abstractmethod
    def channel_type(self) -> str:
        pass
```
---
## def is_running:

```python
    @property
    @abstractmethod
    def is_running(self) -> bool:
        pass
```
---