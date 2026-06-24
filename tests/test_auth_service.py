import pytest
from typing import Optional, List

from app.core.domain.models.curator import Curator
from app.core.domain.models.channel_type import CuratorStatus
from app.core.ports.curator_repository import CuratorRepository
from app.core.services.auth_service import AuthService, AuthError
from app.core.errors.curator import CuratorValidationError


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
        return list(self._curators.values())

    async def update(self, curator: Curator) -> None:
        self._curators[curator.id] = curator

    async def delete(self, curator_id: str) -> None:
        if curator_id in self._curators:
            del self._curators[curator_id]


@pytest.fixture
def repo() -> MockCuratorRepository:
    return MockCuratorRepository()


@pytest.fixture
def auth_service(repo: MockCuratorRepository) -> AuthService:
    return AuthService(repo)


class TestAuthService:
    async def test_register_creates_curator(
        self, auth_service: AuthService, repo: MockCuratorRepository
    ):
        result = await auth_service.register(
            full_name="Test User",
            login="testuser",
            email="test@example.com",
            password="secret123",
        )
        assert "token" in result
        assert result["curator"]["login"] == "testuser"
        assert "password_hash" not in result["curator"]

        saved = await repo.get_by_login("testuser")
        assert saved is not None
        assert saved.password_hash is not None
        assert saved.password_hash != "secret123"

    async def test_register_short_password(self, auth_service: AuthService):
        with pytest.raises(CuratorValidationError, match="не менее 6 символов"):
            await auth_service.register(
                full_name="T", login="t", email="t@t.com", password="12345"
            )

    async def test_register_duplicate_login(self, auth_service: AuthService):
        await auth_service.register(
            full_name="A", login="dup", email="a@a.com", password="secret123"
        )
        with pytest.raises(CuratorValidationError, match="уже существует"):
            await auth_service.register(
                full_name="B", login="dup", email="b@b.com", password="secret123"
            )

    async def test_login_success(self, auth_service: AuthService):
        await auth_service.register(
            full_name="Test", login="test", email="test@test.com", password="secret123"
        )
        result = await auth_service.login(login="test", password="secret123")
        assert "token" in result
        assert result["curator"]["login"] == "test"

    async def test_login_wrong_password(self, auth_service: AuthService):
        await auth_service.register(
            full_name="Test", login="test", email="test@test.com", password="secret123"
        )
        with pytest.raises(AuthError, match="Неверный логин или пароль"):
            await auth_service.login(login="test", password="wrongpass")

    async def test_login_nonexistent_user(self, auth_service: AuthService):
        with pytest.raises(AuthError, match="Неверный логин или пароль"):
            await auth_service.login(login="nobody", password="secret123")

    async def test_login_inactive_curator(
        self, auth_service: AuthService, repo: MockCuratorRepository
    ):
        await auth_service.register(
            full_name="Test", login="test", email="test@test.com", password="secret123"
        )
        curator = await repo.get_by_login("test")
        assert curator is not None
        curator.status = CuratorStatus.INACTIVE
        await repo.update(curator)

        with pytest.raises(AuthError, match="деактивирована"):
            await auth_service.login(login="test", password="secret123")

    async def test_get_current_curator_valid_token(self, auth_service: AuthService):
        result = await auth_service.register(
            full_name="Test", login="test", email="test@test.com", password="secret123"
        )
        curator = await auth_service.get_current_curator(result["token"])
        assert curator.login == "test"

    async def test_get_current_curator_invalid_token(self, auth_service: AuthService):
        with pytest.raises(AuthError, match="Неверный токен"):
            await auth_service.get_current_curator("invalid-token-here")
