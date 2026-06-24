import pytest
from typing import Optional, List

from app.core.domain.models.curator import Curator, AssignmentHistory
from app.core.domain.models.channel_type import CuratorRole, CuratorStatus
from app.core.domain.models.message import Message
from app.core.ports.curator_repository import (
    CuratorRepository,
    AssignmentHistoryRepository,
)
from app.core.ports.message_repository import MessageRepository
from app.core.services.curator_service import CuratorService
from app.core.errors.curator import (
    CuratorNotFoundError,
    CuratorValidationError,
    CuratorAssignmentError,
    CuratorAlreadyAssignedError,
)
from app.core.errors.message import MessageNotFoundError
from app.core.domain.models.channel_type import MessageType


class MockCuratorRepository(CuratorRepository):
    def __init__(self):
        self._curators: dict[str, Curator] = {}

    async def save(self, curator: Curator) -> None:
        self._curators[curator.id] = curator

    async def get_by_id(self, curator_id: str) -> Optional[Curator]:
        return self._curators.get(curator_id)

    async def get_by_login(self, login: str) -> Optional[Curator]:
        for c in self._curators.values():
            if c.login == login:
                return c
        return None

    async def get_all(self, status: Optional[str] = None) -> List[Curator]:
        curators = list(self._curators.values())
        if status:
            curators = [c for c in curators if c.status.value == status]
        return curators

    async def update(self, curator: Curator) -> None:
        if curator.id not in self._curators:
            raise CuratorNotFoundError(curator.id)
        self._curators[curator.id] = curator

    async def delete(self, curator_id: str) -> None:
        if curator_id not in self._curators:
            raise CuratorNotFoundError(curator_id)
        del self._curators[curator_id]


class MockAssignmentHistoryRepository(AssignmentHistoryRepository):
    def __init__(self):
        self._entries: list[AssignmentHistory] = []

    async def save(self, entry: AssignmentHistory) -> None:
        self._entries.append(entry)

    async def get_by_message(self, message_id: str) -> List[AssignmentHistory]:
        return [e for e in self._entries if e.message_id == message_id]

    async def get_by_curator(self, curator_id: str) -> List[AssignmentHistory]:
        return [
            e
            for e in self._entries
            if e.from_curator_id == curator_id or e.to_curator_id == curator_id
        ]

    async def get_current_assignment(
        self, message_id: str
    ) -> Optional[AssignmentHistory]:
        matching = [e for e in self._entries if e.message_id == message_id]
        return matching[-1] if matching else None


class MockMessageRepository(MessageRepository):
    def __init__(self):
        self._messages: dict[str, Message] = {}

    async def save_message(self, message: Message) -> None:
        self._messages[message.id] = message

    async def get_messages(
        self,
        channel: Optional[str] = None,
        sender_id: Optional[str] = None,
        curator_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Message]:
        msgs = list(self._messages.values())
        if curator_id:
            msgs = [m for m in msgs if m.curator_id == curator_id]
        return msgs[offset : offset + limit]

    async def get_message_by_id(self, message_id: str) -> Optional[Message]:
        return self._messages.get(message_id)

    async def update_curator(self, message_id: str, curator_id: Optional[str]) -> None:
        msg = self._messages.get(message_id)
        if msg:
            msg.curator_id = curator_id


@pytest.fixture
def curator_repo() -> MockCuratorRepository:
    return MockCuratorRepository()


@pytest.fixture
def assignment_repo() -> MockAssignmentHistoryRepository:
    return MockAssignmentHistoryRepository()


@pytest.fixture
def message_repo() -> MockMessageRepository:
    return MockMessageRepository()


@pytest.fixture
def service(
    curator_repo: MockCuratorRepository,
    assignment_repo: MockAssignmentHistoryRepository,
    message_repo: MockMessageRepository,
) -> CuratorService:
    return CuratorService(curator_repo, assignment_repo, message_repo)


def make_curator(**kwargs) -> Curator:
    return Curator(
        id=kwargs.get("id", "curator:test"),
        full_name=kwargs.get("full_name", "Test Curator"),
        login=kwargs.get("login", "testcurator"),
        email=kwargs.get("email", "test@example.com"),
        role=kwargs.get("role", CuratorRole.AGENT),
        status=kwargs.get("status", CuratorStatus.ACTIVE),
    )


def make_message(**kwargs) -> Message:
    return Message(
        id=kwargs.get("id", "msg:test"),
        channel=kwargs.get("channel", "telegram"),
        sender_id=kwargs.get("sender_id", "user1"),
        content=kwargs.get("content", "Test message"),
        timestamp=kwargs.get("timestamp", "2024-01-01T00:00:00"),
        message_type=kwargs.get("message_type", MessageType.TEXT),
        metadata=kwargs.get("metadata", {}),
        curator_id=kwargs.get("curator_id"),
    )


class TestCuratorService:
    async def test_create_curator(
        self, service: CuratorService, curator_repo: MockCuratorRepository
    ):
        curator = await service.create_curator(
            full_name="Иван Иванов",
            login="ivanov",
            email="ivanov@example.com",
        )
        assert curator.id.startswith("curator:")
        assert curator.full_name == "Иван Иванов"
        assert curator.login == "ivanov"
        assert curator.email == "ivanov@example.com"
        assert curator.role == CuratorRole.AGENT
        assert curator.status == CuratorStatus.ACTIVE

        saved = await curator_repo.get_by_id(curator.id)
        assert saved is not None
        assert saved.full_name == "Иван Иванов"

    async def test_create_curator_empty_name(self, service: CuratorService):
        with pytest.raises(CuratorValidationError, match="ФИО не может быть пустым"):
            await service.create_curator(
                full_name="", login="test", email="test@test.com"
            )

    async def test_create_curator_duplicate_login(self, service: CuratorService):
        await service.create_curator(
            full_name="User1", login="duplicate", email="u1@test.com"
        )
        with pytest.raises(CuratorValidationError, match="уже существует"):
            await service.create_curator(
                full_name="User2", login="duplicate", email="u2@test.com"
            )

    async def test_create_curator_with_role(self, service: CuratorService):
        curator = await service.create_curator(
            full_name="Admin", login="admin", email="admin@test.com", role="admin"
        )
        assert curator.role == CuratorRole.ADMIN

    async def test_get_curator(
        self, service: CuratorService, curator_repo: MockCuratorRepository
    ):
        curator = await service.create_curator(
            full_name="Test", login="test", email="test@test.com"
        )
        found = await service.get_curator(curator.id)
        assert found is not None
        assert found.id == curator.id

    async def test_get_curator_not_found(self, service: CuratorService):
        with pytest.raises(CuratorNotFoundError, match="not found"):
            await service.get_curator("curator:nonexistent")

    async def test_get_all_curators(self, service: CuratorService):
        await service.create_curator(full_name="A", login="a", email="a@test.com")
        await service.create_curator(full_name="B", login="b", email="b@test.com")
        curators = await service.get_all_curators()
        assert len(curators) == 2

    async def test_get_all_curators_filter_by_status(self, service: CuratorService):
        c1 = await service.create_curator(
            full_name="Active", login="active", email="a@test.com"
        )
        await service.update_curator(c1.id, {"status": "inactive"})
        await service.create_curator(
            full_name="Active2", login="active2", email="a2@test.com"
        )

        active = await service.get_all_curators(status="active")
        assert len(active) == 1
        inactive = await service.get_all_curators(status="inactive")
        assert len(inactive) == 1

    async def test_update_curator(self, service: CuratorService):
        curator = await service.create_curator(
            full_name="Old", login="old", email="old@test.com"
        )
        updated = await service.update_curator(
            curator.id, {"full_name": "New", "login": "new"}
        )
        assert updated.full_name == "New"
        assert updated.login == "new"

    async def test_update_curator_not_found(self, service: CuratorService):
        with pytest.raises(CuratorNotFoundError):
            await service.update_curator("curator:none", {"full_name": "X"})

    async def test_set_curator_status(self, service: CuratorService):
        curator = await service.create_curator(
            full_name="T", login="t", email="t@test.com"
        )
        updated = await service.set_curator_status(curator.id, "inactive")
        assert updated.status == CuratorStatus.INACTIVE

    async def test_delete_curator(
        self, service: CuratorService, curator_repo: MockCuratorRepository
    ):
        curator = await service.create_curator(
            full_name="T", login="t", email="t@test.com"
        )
        await service.delete_curator(curator.id)
        assert await curator_repo.get_by_id(curator.id) is None

    async def test_assign_curator_to_message(
        self, service: CuratorService, message_repo: MockMessageRepository
    ):
        curator = await service.create_curator(
            full_name="Curator", login="cur", email="c@test.com"
        )
        msg = make_message(id="msg:1")
        await message_repo.save_message(msg)

        result = await service.assign_curator_to_message("msg:1", curator.id)
        assert result.curator_id == curator.id

        updated = await message_repo.get_message_by_id("msg:1")
        assert updated is not None
        assert updated.curator_id == curator.id

    async def test_assign_curator_to_nonexistent_message(self, service: CuratorService):
        curator = await service.create_curator(
            full_name="T", login="t", email="t@test.com"
        )
        with pytest.raises(MessageNotFoundError):
            await service.assign_curator_to_message("msg:none", curator.id)

    async def test_assign_nonexistent_curator(
        self, service: CuratorService, message_repo: MockMessageRepository
    ):
        msg = make_message(id="msg:1")
        await message_repo.save_message(msg)
        with pytest.raises(CuratorNotFoundError):
            await service.assign_curator_to_message("msg:1", "curator:none")

    async def test_assign_inactive_curator(
        self, service: CuratorService, message_repo: MockMessageRepository
    ):
        curator = await service.create_curator(
            full_name="T", login="t", email="t@test.com"
        )
        await service.set_curator_status(curator.id, "inactive")
        msg = make_message(id="msg:1")
        await message_repo.save_message(msg)
        with pytest.raises(CuratorAssignmentError, match="неактивного"):
            await service.assign_curator_to_message("msg:1", curator.id)

    async def test_assign_same_curator_twice(
        self, service: CuratorService, message_repo: MockMessageRepository
    ):
        curator = await service.create_curator(
            full_name="T", login="t", email="t@test.com"
        )
        msg = make_message(id="msg:1")
        await message_repo.save_message(msg)
        await service.assign_curator_to_message("msg:1", curator.id)
        with pytest.raises(CuratorAlreadyAssignedError):
            await service.assign_curator_to_message("msg:1", curator.id)

    async def test_transfer_message(
        self, service: CuratorService, message_repo: MockMessageRepository
    ):
        c1 = await service.create_curator(
            full_name="C1", login="c1", email="c1@test.com"
        )
        c2 = await service.create_curator(
            full_name="C2", login="c2", email="c2@test.com"
        )
        msg = make_message(id="msg:1", curator_id=c1.id)
        await message_repo.save_message(msg)

        result = await service.transfer_message("msg:1", c1.id, c2.id)
        assert result.curator_id == c2.id

    async def test_transfer_message_saves_history(
        self,
        service: CuratorService,
        message_repo: MockMessageRepository,
        assignment_repo: MockAssignmentHistoryRepository,
    ):
        c1 = await service.create_curator(
            full_name="C1", login="c1", email="c1@test.com"
        )
        c2 = await service.create_curator(
            full_name="C2", login="c2", email="c2@test.com"
        )
        msg = make_message(id="msg:1", curator_id=c1.id)
        await message_repo.save_message(msg)

        await service.transfer_message(
            "msg:1", c1.id, c2.id, reason="Передача по нагрузке"
        )
        history = await assignment_repo.get_by_message("msg:1")
        assert len(history) == 1
        assert history[0].from_curator_id == c1.id
        assert history[0].to_curator_id == c2.id
        assert history[0].reason == "Передача по нагрузке"

    async def test_get_messages_by_curator(
        self, service: CuratorService, message_repo: MockMessageRepository
    ):
        curator = await service.create_curator(
            full_name="T", login="t", email="t@test.com"
        )
        await message_repo.save_message(make_message(id="msg:1", curator_id=curator.id))
        await message_repo.save_message(make_message(id="msg:2", curator_id=curator.id))
        await message_repo.save_message(make_message(id="msg:3"))

        msgs = await service.get_messages_by_curator(curator.id)
        assert len(msgs) == 2
        assert all(m.curator_id == curator.id for m in msgs)

    async def test_get_assignment_history(
        self,
        service: CuratorService,
        message_repo: MockMessageRepository,
        assignment_repo: MockAssignmentHistoryRepository,
    ):
        c1 = await service.create_curator(
            full_name="C1", login="c1", email="c1@test.com"
        )
        c2 = await service.create_curator(
            full_name="C2", login="c2", email="c2@test.com"
        )
        msg = make_message(id="msg:1")
        await message_repo.save_message(msg)

        await service.assign_curator_to_message("msg:1", c1.id)
        await service.transfer_message("msg:1", c1.id, c2.id)

        history = await service.get_message_assignment_history("msg:1")
        assert len(history) == 2
