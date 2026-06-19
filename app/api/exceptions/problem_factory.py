from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.config import config as app_config


@dataclass(slots=True, frozen=True)
class ErrorMeta:
    code: str
    title: str
    status: int

    def to_problem(self, detail: str, base_uri: str, **extra: Any) -> dict[str, Any]:
        result = {
            "type": f"{base_uri}/{self.code}",
            "title": self.title,
            "status": self.status,
            "detail": detail,
        }
        result.update(extra)
        return result


class ErrorCode(Enum):
    MESSAGE_NOT_FOUND = ErrorMeta("message-not-found", "Сообщение не найдено", 404)
    CHANNEL_NOT_FOUND = ErrorMeta("channel-not-found", "Канал не найден", 404)

    VALIDATION_ERROR = ErrorMeta("validation-error", "Ошибка валидации данных", 400)

    SERVER_ERROR = ErrorMeta("server-error", "Внутренняя ошибка сервера", 500)
    ENGINE_ERROR = ErrorMeta("engine-error", "Ошибка работы движка", 500)
    SERVICE_CONNECTION_ERROR = ErrorMeta(
        "service-connection-error", "Ошибка подключения к сервису", 500
    )


class ProblemFactory:
    __slots__ = ("_base_uri",)

    def __init__(self, config: Any = app_config) -> None:
        self._base_uri = config.app.base_problem_uri

    def build(self, error: ErrorCode, detail: str, **extra: Any) -> dict[str, Any]:
        return error.value.to_problem(detail, self._base_uri, **extra)


problem_factory = ProblemFactory()
