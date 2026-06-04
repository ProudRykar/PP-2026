## Класс DatabaseGateway


```python
class DatabaseGateway(ABC):
```

---
## def init:

```python
    @abstractmethod
    async def init(self) -> None:
        pass
```
---
## def close:

```python
    @abstractmethod
    async def close(self) -> None:
        pass
```
---
## def get_session:

```python
    @abstractmethod
    def get_session(self) -> AbstractAsyncContextManager[AsyncSession]:
        pass
```
---