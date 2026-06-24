from typing import Callable, Type, Any

from litestar import Request, Response

from app.api.exceptions.problem_factory import (
    ErrorCode,
    ProblemFactory,
    problem_factory,
)
from app.core.errors.message import MessageNotFoundError
from app.core.errors.curator import (
    CuratorNotFoundError,
    CuratorValidationError,
    CuratorAssignmentError,
    CuratorAlreadyAssignedError,
)
from app.core.errors.validation import (
    FileValidationError,
    FileExtensionValidationError,
    FileSizeValidationError,
    MessageValidationError,
    ClientValidationError,
    EmailValidationError,
)


def create_problem_response(
    body: dict[str, Any],
    headers: dict[str, str] | None = None,
) -> Response:
    return Response(
        content=body,
        status_code=body["status"],
        media_type="application/problem+json",
        headers=headers,
    )


def create_handler(
    error_code: ErrorCode,
    factory: ProblemFactory = problem_factory,
) -> Callable[[Request, Exception], Response]:
    def handler(request: Request, exc: Exception) -> Response:
        detail = str(getattr(exc, "message", str(exc)))
        body = factory.build(error_code, detail)
        return create_problem_response(body)

    return handler


ERROR_MAPPING: dict[ErrorCode, tuple[type[Exception], ...]] = {
    ErrorCode.MESSAGE_NOT_FOUND: (MessageNotFoundError,),
    ErrorCode.CURATOR_NOT_FOUND: (CuratorNotFoundError,),
    ErrorCode.VALIDATION_ERROR: (
        FileValidationError,
        FileExtensionValidationError,
        FileSizeValidationError,
        MessageValidationError,
        ClientValidationError,
        EmailValidationError,
        CuratorValidationError,
        CuratorAssignmentError,
        CuratorAlreadyAssignedError,
    ),
}


def build_exception_handlers() -> dict[Type[Exception], Callable]:
    handlers: dict[Type[Exception], Callable] = {}

    for error_code, exceptions in ERROR_MAPPING.items():
        handler = create_handler(error_code)
        for exc_type in exceptions:
            handlers[exc_type] = handler

    return handlers


EXCEPTION_HANDLERS = build_exception_handlers()
