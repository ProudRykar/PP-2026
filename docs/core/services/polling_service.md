## Класс PollingOrchestrator


```python
class PollingOrchestrator(AbstractPollingService):
```

---
## def init:

```python
    def __init__(self, message_service: MessageService):
        self._message_service = message_service
        self._engines: List[MessageEngine] = []
        self._running = False
        self._tasks: List[asyncio.Task] = []
```
---
## def register_engine:

```python
    def register_engine(self, engine: MessageEngine) -> None:
        self._engines.append(engine)
        logger.info(f"Engine registered: {engine.channel_type}")
```
---
## async def start_polling:

```python
    async def start_polling(self) -> None:
        self._running = True
        for engine in self._engines:
            await engine.start()
            task = asyncio.create_task(self._poll_engine(engine))
            self._tasks.append(task)
            logger.info(f"Polling started for {engine.channel_type}")

        logger.info(f"Polling started for {len(self._engines)} engines")
```
---
## async def stop_polling:

```python
    async def stop_polling(self) -> None:
        self._running = False
        for engine in self._engines:
            try:
                await engine.stop()
            except Exception as e:
                logger.error(f"Error stopping engine {engine.channel_type}: {e}")

        for task in self._tasks:
            task.cancel()

        self._tasks.clear()
        logger.info("Polling stopped")
```
---
## async def _poll_engine:

```python
    async def _poll_engine(self, engine: MessageEngine) -> None:
        try:
            async for message in engine.get_incoming():
                if message:
                    try:
                        await self._message_service.save_message(message)
                        logger.debug(f"Message from {engine.channel_type} saved")
                    except Exception as e:
                        logger.error(
                            f"Error saving message from {engine.channel_type}: {e}"
                        )
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error polling {engine.channel_type}: {e}")
        finally:
            try:
                if engine.is_running:
                    await engine.stop()
            except Exception as e:
                logger.error(f"Error stopping {engine.channel_type}: {e}")
```
---