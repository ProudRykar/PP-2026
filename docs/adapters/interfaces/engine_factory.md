## Класс EngineFactory


```python
class EngineFactory(ABC):
```

---
## def create_engine:

```python
    @abstractmethod
    def create_engine(self, config: dict) -> MessageEngine:
        pass
```
---
## def get_supported_channel:

```python
    @abstractmethod
    def get_supported_channel(self) -> str:
        pass
```
---