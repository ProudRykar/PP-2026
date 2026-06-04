## Класс BaseEngine


```python
class BaseEngine(MessageEngine):
```

---
## def init:

```python
    def __init__(self, channel_type: str):
        self._channel_type = channel_type
        self._running = False
```
---
## async def start:

```python
    async def start(self) -> None:
        self._running = True
        logger.info(f"{self._channel_type} engine started")
```
---
## async def stop:

```python
    async def stop(self) -> None:
        self._running = False
        logger.info(f"{self._channel_type} engine stopped")
```
---
## async def get_incoming:

```python
    async def get_incoming(self) -> AsyncGenerator[Message, None]:
        if not self._running:
            return
        if False:
            yield
```
---
## def channel_type:

```python
    @property
    def channel_type(self) -> str:
        return self._channel_type
```
---
## def is_running:

```python
    @property
    def is_running(self) -> bool:
        return self._running
```
---
## def _generate_message_id:

```python
    def _generate_message_id(self, original_id: str) -> str:
        return f"{self._channel_type}:{original_id}"
```
---