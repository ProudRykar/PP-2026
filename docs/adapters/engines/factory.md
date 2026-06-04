## Класс TelegramEngineFactory


```python
class TelegramEngineFactory(EngineFactory):
```

---
## def create_engine:

```python
    def create_engine(self, config: dict) -> MessageEngine:
        token = config.get("token")
        if not token:
            raise ValueError("Telegram token is required")
        return TelegramEngine(token=token)
```
---
## def get_supported_channel:

```python
    def get_supported_channel(self) -> str:
        return ChannelType.TELEGRAM
```
---
## Класс EmailEngineFactory


```python
class EmailEngineFactory(EngineFactory):
```

---
## def create_engine:

```python
    def create_engine(self, config: dict) -> MessageEngine:
        required = ["host", "port", "user", "password"]
        for key in required:
            if key not in config:
                raise ValueError(f"Email config missing: {key}")

        return EmailEngine(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            poll_interval=config.get("poll_interval", 60),
        )
```
---
## def get_supported_channel:

```python
    def get_supported_channel(self) -> str:
        return ChannelType.EMAIL
```
---
## Класс EngineAbstractFactory


```python
class EngineAbstractFactory:
```

---
## def init:

```python
    def __init__(self):
        self._factories: Dict[str, EngineFactory] = {}
```
---
## def register_factory:

```python
    def register_factory(self, factory: EngineFactory) -> None:
        channel = factory.get_supported_channel()
        self._factories[channel] = factory
        logger.info(f"Factory registered for channel: {channel}")
```
---
## def create_engine:

```python
    def create_engine(
        self, channel_type: str, config: dict
    ) -> MessageEngine:
        if channel_type not in self._factories:
            raise ValueError(
                f"No factory registered for channel: {channel_type}"
            )

        engine = self._factories[channel_type].create_engine(config)
        logger.info(f"Created engine {channel_type}")
        return engine
```
---
## def get_supported_channels:

```python
    def get_supported_channels(self) -> list:
        return list(self._factories.keys())
```
---