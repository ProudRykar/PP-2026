## Класс TelegramEngine


```python
class TelegramEngine(MessageEngine):
```

---
## def init:

```python
    def __init__(self, token: str):
        self._token = token
        self._app: Application = None
        self._running = False
        self._channel_type = ChannelType.TELEGRAM
        self._queue: asyncio.Queue[Message] = asyncio.Queue()
```
---
## async def start:

```python
    async def start(self) -> None:
        self._app = Application.builder().token(self._token).build()
        self._app.add_handler(MessageHandler(filters.ALL, self._handle_message))
        await self._app.initialize()
        await self._app.start()
        await self._app.updater.start_polling()
        self._running = True
        logger.info("Telegram engine started")
```
---
## async def stop:

```python
    async def stop(self) -> None:
        if self._app:
            await self._app.updater.stop()
            await self._app.stop()
            await self._app.shutdown()
        self._running = False
        logger.info("Telegram engine stopped")
```
---
## async def send_message:

```python
    async def send_message(self, recipient: str, content: str, **kwargs) -> str:
        bot = Bot(self._token)
        sent = await bot.send_message(chat_id=recipient, text=content)
        return str(sent.message_id)
```
---
## async def get_incoming:

```python
    async def get_incoming(self) -> AsyncGenerator[Message, None]:
        while self._running:
            try:
                message = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                yield message
            except asyncio.TimeoutError:
                continue
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
## async def _handle_message:

```python
    async def _handle_message(self, update, context) -> None:
        if not update.message:
            return

        msg = update.message
        message = Message(
            id=f"telegram:{msg.message_id}",
            channel=self._channel_type,
            sender=str(msg.from_user.id),
            content=msg.text or "",
            timestamp=msg.date,
            metadata={
                "chat_id": msg.chat_id,
                "message_id": msg.message_id,
                "username": msg.from_user.username,
                "first_name": msg.from_user.first_name,
            },
        )
        logger.info(f"Received message from Telegram: {message.id}")
        await self._queue.put(message)
```
---