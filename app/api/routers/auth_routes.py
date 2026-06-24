import logging
from dataclasses import dataclass

from litestar import Controller, post, get
from litestar.exceptions import HTTPException
from litestar.params import Parameter

from app.core.services.auth_service import AuthService, AuthError
from app.core.errors.curator import CuratorValidationError

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RegisterRequest:
    full_name: str
    login: str
    email: str
    password: str
    role: str = "agent"


@dataclass(slots=True)
class LoginRequest:
    login: str
    password: str


@dataclass(slots=True)
class AuthResponse:
    token: str
    curator: dict


class AuthController(Controller):
    path = "/api/auth"

    @post("/register")
    async def register(
        self,
        auth_service: AuthService,
        data: RegisterRequest,
    ) -> AuthResponse:
        try:
            result = await auth_service.register(
                full_name=data.full_name,
                login=data.login,
                email=data.email,
                password=data.password,
                role=data.role,
            )
            return AuthResponse(token=result["token"], curator=result["curator"])
        except CuratorValidationError as e:
            raise HTTPException(status_code=400, detail=e.message)

    @post("/login")
    async def login(
        self,
        auth_service: AuthService,
        data: LoginRequest,
    ) -> AuthResponse:
        try:
            result = await auth_service.login(
                login=data.login,
                password=data.password,
            )
            return AuthResponse(token=result["token"], curator=result["curator"])
        except AuthError as e:
            raise HTTPException(status_code=401, detail=e.message)

    @get("/me")
    async def me(
        self,
        auth_service: AuthService,
        authorization: str = Parameter(default=None, header="Authorization"),
    ) -> AuthResponse:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Требуется авторизация")
        token = authorization[7:]
        try:
            curator = await auth_service.get_current_curator(token)
            return AuthResponse(token=token, curator=curator.to_dict())
        except AuthError as e:
            raise HTTPException(status_code=401, detail=e.message)
