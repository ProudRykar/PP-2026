import logging
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import bcrypt
import jwt

from app.config import config as app_config
from app.core.domain.models.curator import Curator
from app.core.domain.models.channel_type import CuratorRole, CuratorStatus
from app.core.ports.curator_repository import CuratorRepository
from app.core.errors.curator import CuratorValidationError

logger = logging.getLogger(__name__)


class AuthError(Exception):
    def __init__(self, message: str = "Ошибка аутентификации") -> None:
        self.message = message
        super().__init__(self.message)


class AuthService:
    def __init__(self, curator_repository: CuratorRepository):
        self._curator_repo = curator_repository

    def _hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def _verify_password(self, password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode(), password_hash.encode())

    def _create_token(self, curator_id: str) -> str:
        cfg = app_config.auth
        payload = {
            "sub": curator_id,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=cfg.access_token_expire_minutes),
        }
        return jwt.encode(payload, cfg.jwt_secret, algorithm=cfg.jwt_algorithm)

    def decode_token(self, token: str) -> str:
        cfg = app_config.auth
        try:
            payload = jwt.decode(token, cfg.jwt_secret, algorithms=[cfg.jwt_algorithm])
            curator_id = payload.get("sub")
            if not curator_id:
                raise AuthError("Неверный токен")
            return curator_id
        except jwt.ExpiredSignatureError:
            raise AuthError("Срок действия токена истёк")
        except jwt.InvalidTokenError:
            raise AuthError("Неверный токен")

    async def register(
        self,
        full_name: str,
        login: str,
        email: str,
        password: str,
        role: str = "agent",
    ) -> dict:
        if not password or len(password) < 6:
            raise CuratorValidationError("Пароль должен быть не менее 6 символов")

        existing = await self._curator_repo.get_by_login(login)
        if existing:
            raise CuratorValidationError(f"Куратор с логином '{login}' уже существует")

        try:
            parsed_role = CuratorRole(role)
        except ValueError:
            parsed_role = CuratorRole.AGENT

        curator = Curator(
            id=f"curator:{uuid4().hex}",
            full_name=full_name.strip(),
            login=login.strip(),
            email=email.strip(),
            password_hash=self._hash_password(password),
            role=parsed_role,
        )
        await self._curator_repo.save(curator)
        token = self._create_token(curator.id)
        logger.info(f"Curator registered: {curator.id} ({curator.login})")
        return {"token": token, "curator": curator.to_dict()}

    async def login(self, login: str, password: str) -> dict:
        curator = await self._curator_repo.get_by_login(login.strip())
        if not curator:
            raise AuthError("Неверный логин или пароль")
        if curator.status != CuratorStatus.ACTIVE:
            raise AuthError("Учётная запись деактивирована")
        if not curator.password_hash or not self._verify_password(
            password, curator.password_hash
        ):
            raise AuthError("Неверный логин или пароль")

        curator.last_activity = datetime.now(timezone.utc)
        await self._curator_repo.update(curator)

        token = self._create_token(curator.id)
        logger.info(f"Curator logged in: {curator.id} ({curator.login})")
        return {"token": token, "curator": curator.to_dict()}

    async def get_current_curator(self, token: str) -> Curator:
        curator_id = self.decode_token(token)
        curator = await self._curator_repo.get_by_id(curator_id)
        if not curator:
            raise AuthError("Куратор не найден")
        if curator.status != CuratorStatus.ACTIVE:
            raise AuthError("Учётная запись деактивирована")
        return curator
