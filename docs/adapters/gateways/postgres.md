## Класс PostgresDatabaseGateway


```python
class PostgresDatabaseGateway(DatabaseGateway):
```

---
## def init:

```python
    def __init__(self):
        self._engine = None
        self._session_factory = None
```
---
## async def init:

```python
    async def init(self) -> None:
        url = get_database_url()
        self._engine = create_async_engine(
            url,
            echo=os.getenv("DEBUG", "false").lower() == "true",
            pool_size=10,
            max_overflow=20,
            poolclass=NullPool if os.getenv("TESTING") else None,
        )
        self._session_factory = async_sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized")
```
---
## async def close:

```python
    async def close(self) -> None:
        if self._engine:
            await self._engine.dispose()
            self._engine = None
        logger.info("Database closed")
```
---
## def get_session:

```python
    @asynccontextmanager
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        if self._session_factory is None:
            raise RuntimeError("Database not initialized. Call init() first.")
        async with self._session_factory() as s:
            try:
                yield s
                await s.commit()
            except Exception:
                await s.rollback()
                raise
```
---
## def get_database_url:

```python
def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL is not set")
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url
```
---