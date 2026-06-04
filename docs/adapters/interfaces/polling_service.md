## Класс PollingService


```python
class PollingService(ABC):
```

---
## def start_polling:

```python
    @abstractmethod
    async def start_polling(self) -> None:
        pass
```
---
## def stop_polling:

```python
    @abstractmethod
    async def stop_polling(self) -> None:
        pass
```
---
## def register_engine:

```python
    @abstractmethod
    def register_engine(self, engine: MessageEngine) -> None:
        pass
```
---