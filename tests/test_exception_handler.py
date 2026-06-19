import pytest
from unittest.mock import MagicMock
from litestar import Request, Response

from app.api.exceptions.handlers import (
    ErrorCode,
    create_problem_response,
    create_handler,
    EXCEPTION_HANDLERS,
)
from app.api.exceptions.problem_factory import problem_factory
from app.core.errors.message import MessageNotFoundError


def test_create_problem_response_sets_status_and_media_type():
    body = problem_factory.build(ErrorCode.MESSAGE_NOT_FOUND, "not found")
    resp = create_problem_response(body)

    assert isinstance(resp, Response)
    assert resp.status_code == body["status"]
    assert resp.media_type == "application/problem+json"
    assert resp.content == body


def test_create_handler_uses_exc_message_attr_when_present():
    class MyExc(Exception):
        def __init__(self, message: str):
            super().__init__("ignored")
            self.message = message

    handler = create_handler(ErrorCode.MESSAGE_NOT_FOUND)
    resp = handler(request=MagicMock(spec=Request), exc=MyExc("nope"))

    assert isinstance(resp, Response)
    assert resp.status_code == 404
    assert resp.media_type == "application/problem+json"
    assert resp.content["detail"] == "nope"


def test_create_handler_falls_back_to_str_exc_when_no_message_attr():
    handler = create_handler(ErrorCode.SERVER_ERROR)
    resp = handler(request=MagicMock(spec=Request), exc=Exception("boom"))

    assert isinstance(resp, Response)
    assert resp.status_code == 500
    assert resp.media_type == "application/problem+json"
    assert resp.content["detail"] == "boom"


def test_exception_handlers_mapping_contains_expected_keys():
    assert MessageNotFoundError in EXCEPTION_HANDLERS


def test_exception_handlers_use_correct_handler_type():
    handler = EXCEPTION_HANDLERS[MessageNotFoundError]

    resp = handler(
        request=MagicMock(spec=Request),
        exc=MessageNotFoundError("msg:123"),
    )

    assert isinstance(resp, Response)
    assert resp.status_code == 404
    assert resp.media_type == "application/problem+json"


@pytest.mark.parametrize(
    ("enum_item", "code", "title", "status"),
    [
        (ErrorCode.MESSAGE_NOT_FOUND, "message-not-found", "Сообщение не найдено", 404),
        (ErrorCode.CHANNEL_NOT_FOUND, "channel-not-found", "Канал не найден", 404),
        (
            ErrorCode.VALIDATION_ERROR,
            "validation-error",
            "Ошибка валидации данных",
            400,
        ),
        (ErrorCode.SERVER_ERROR, "server-error", "Внутренняя ошибка сервера", 500),
        (ErrorCode.ENGINE_ERROR, "engine-error", "Ошибка работы движка", 500),
        (
            ErrorCode.SERVICE_CONNECTION_ERROR,
            "service-connection-error",
            "Ошибка подключения к сервису",
            500,
        ),
    ],
)
def test_error_codes_fields(enum_item, code, title, status):
    assert enum_item.value.code == code
    assert enum_item.value.title == title
    assert enum_item.value.status == status


def test_problem_factory_build():
    detail = "Сообщение не найдено"
    body = problem_factory.build(ErrorCode.MESSAGE_NOT_FOUND, detail)

    assert body == {
        "type": f"{problem_factory._base_uri}/message-not-found",
        "title": "Сообщение не найдено",
        "status": 404,
        "detail": detail,
    }


def test_problem_factory_detail_not_modified():
    detail = "  special chars: !@#$  "
    body = problem_factory.build(ErrorCode.SERVER_ERROR, detail)
    assert body["detail"] == detail


def test_problem_factory_expected_keys():
    body = problem_factory.build(ErrorCode.MESSAGE_NOT_FOUND, "no msg")
    assert set(body.keys()) == {"type", "title", "status", "detail"}
