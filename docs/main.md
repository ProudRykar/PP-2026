## def create_engines_from_env:

```python
def create_engines_from_env(abstract_factory: EngineAbstractFactory):
    engines = []

    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if tg_token and tg_token != "your_telegram_bot_token_here":
        try:
            engine = abstract_factory.create_engine("telegram", {"token": tg_token})
            engines.append(engine)
            logger.info("Telegram engine created")
        except Exception as e:
            logger.error(f"Error creating Telegram engine: {e}")

    email_host = os.getenv("EMAIL_HOST")
    if email_host:
        try:
            engine = abstract_factory.create_engine(
                "email",
                {
                    "host": email_host,
                    "port": int(os.getenv("EMAIL_PORT", 993)),
                    "user": os.getenv("EMAIL_USER"),
                    "password": os.getenv("EMAIL_PASSWORD"),
                    "poll_interval": int(os.getenv("EMAIL_POLL_INTERVAL", 60)),
                },
            )
            engines.append(engine)
            logger.info("Email engine created")
        except Exception as e:
            logger.error(f"Error creating Email engine: {e}")

    return engines
```
---
## def lifespan:

```python
@asynccontextmanager
async def lifespan(app: Litestar):
    logger.info("Starting application...")

    container = get_container()

    db = container.resolve(DatabaseGateway)
    await db.init()
    logger.info("Database initialized")

    abstract_factory = initialize_factories(container)

    engines = create_engines_from_env(abstract_factory)

    if engines:
        polling_service = container.resolve(PollingService)
        for engine in engines:
            try:
                polling_service.register_engine(engine)
            except Exception as e:
                logger.error(f"Error registering engine: {e}")

        asyncio.create_task(polling_service.start_polling())
        logger.info(f"Polling started for {len(engines)} engines")
    else:
        logger.warning("No engines configured! Check .env file")

    yield

    logger.info("Shutting down...")
    if engines:
        polling_service = container.resolve(PollingService)
        await polling_service.stop_polling()
    await db.close()
    logger.info("Application shut down")
```
---
## def message_not_found_handler:

```python
def message_not_found_handler(request, exc: MessageNotFoundError):
    from litestar import Response

    return Response(content={"detail": str(exc)}, status_code=HTTP_404_NOT_FOUND)
```
---
## def websocket_handler:
#### Маршрут:
- **Декоратор:** @websocket
- **Маршрут:** `/ws`


```python
@websocket("/ws")
async def websocket_handler(socket: WebSocket) -> None:
    await socket.accept()
    websocket_connections.append(socket)
    try:
        while True:
            await socket.receive_text()
    except Exception:
        websocket_connections.remove(socket)
```
---
## async def broadcast_message:

```python
async def broadcast_message(message: dict):
    for connection in websocket_connections:
        try:
            await connection.send_json(message)
        except Exception:
            pass
```
---