from abc import ABC, abstractmethod
from typing import Optional, List

from app.core.domain.models.curator import Curator, AssignmentHistory


class CuratorRepository(ABC):
    @abstractmethod
    async def save(self, curator: Curator) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, curator_id: str) -> Optional[Curator]:
        pass

    @abstractmethod
    async def get_by_login(self, login: str) -> Optional[Curator]:
        pass

    @abstractmethod
    async def get_all(self, status: Optional[str] = None) -> List[Curator]:
        pass

    @abstractmethod
    async def update(self, curator: Curator) -> None:
        pass

    @abstractmethod
    async def delete(self, curator_id: str) -> None:
        pass


class AssignmentHistoryRepository(ABC):
    @abstractmethod
    async def save(self, entry: AssignmentHistory) -> None:
        pass

    @abstractmethod
    async def get_by_message(self, message_id: str) -> List[AssignmentHistory]:
        pass

    @abstractmethod
    async def get_by_curator(self, curator_id: str) -> List[AssignmentHistory]:
        pass

    @abstractmethod
    async def get_current_assignment(
        self, message_id: str
    ) -> Optional[AssignmentHistory]:
        pass
