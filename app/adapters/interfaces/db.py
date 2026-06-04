from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager

from sqlalchemy.ext.asyncio import AsyncSession


class DatabaseGateway(ABC):
    @abstractmethod
    async def init(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    @abstractmethod
    def get_session(self) -> AbstractAsyncContextManager[AsyncSession]:
        pass
