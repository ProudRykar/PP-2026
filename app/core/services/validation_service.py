import logging
import os
import re

from app.config import config as app_config
from app.core.errors.validation import (
    ClientValidationError,
    EmailValidationError,
    FileExtensionValidationError,
    FileSizeValidationError,
    FileValidationError,
    MessageValidationError,
)

logger = logging.getLogger(__name__)


class FileValidator:
    EXTENSION_TO_CONTENT_TYPE: dict[str, str] = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
        "mp4": "video/mp4",
        "webm": "video/webm",
        "pdf": "application/pdf",
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xls": "application/vnd.ms-excel",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "txt": "text/plain",
        "csv": "text/csv",
    }

    def __init__(self, config=app_config) -> None:
        self._config = config
        self._allowed_extensions: frozenset[str] = frozenset(
            ext.lower().lstrip(".")
            for ext in config.validation.ALLOWED_UPLOAD_EXTENSIONS
        )
        self._max_file_size: int = config.validation.MAX_FILE_SIZE

    def validate_file(self, filename: str, content_type: str, data: bytes) -> str:
        ext = self._validate_filename(filename)
        self._validate_extension(ext)
        self._validate_content_type(ext, content_type)
        self._validate_file_size(data)
        return ext

    def _validate_filename(self, filename: str) -> str:
        if not filename or not filename.strip():
            raise FileValidationError("Имя файла не может быть пустым")
        _, ext = os.path.splitext(filename)
        ext = ext.lower().lstrip(".")
        if not ext:
            raise FileValidationError("Файл должен иметь расширение")
        return ext

    def _validate_extension(self, ext: str) -> None:
        if ext not in self._allowed_extensions:
            allowed = ", ".join(f".{e}" for e in sorted(self._allowed_extensions))
            raise FileExtensionValidationError(
                f"Недопустимое расширение .{ext}. Разрешены: {allowed}"
            )

    def _validate_content_type(self, ext: str, content_type: str) -> None:
        expected = self.EXTENSION_TO_CONTENT_TYPE.get(ext)
        if (
            expected
            and content_type != expected
            and content_type != "application/octet-stream"
        ):
            logger.debug(
                "Content-Type mismatch: expected %s, got %s for .%s",
                expected,
                content_type,
                ext,
            )

    def _validate_file_size(self, data: bytes) -> None:
        if len(data) > self._max_file_size:
            size_mb = self._max_file_size / (1024 * 1024)
            raise FileSizeValidationError(
                f"Файл превышает максимальный размер {size_mb:.0f} МБ"
            )


class MessageValidator:
    def __init__(self, config=app_config) -> None:
        self._config = config
        self._max_content_length: int = config.validation.MAX_MESSAGE_LENGTH

    def validate_content(self, content: str | None) -> str:
        if not content:
            raise MessageValidationError("Сообщение не может быть пустым")
        content = content.strip()
        if not content:
            raise MessageValidationError("Сообщение не может быть пустым")
        if len(content) > self._max_content_length:
            raise MessageValidationError(
                f"Сообщение не должно превышать {self._max_content_length} символов"
            )
        return content


class ClientValidator:
    EMAIL_REGEX: re.Pattern[str] = re.compile(
        r"^(?=.{1,64}@)[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )
    PHONE_REGEX: re.Pattern[str] = re.compile(r"^\+?[0-9]{7,15}$")

    def __init__(self, config=app_config) -> None:
        self._config = config

    def validate_name(self, name: str | None) -> str:
        if not name or not name.strip():
            raise ClientValidationError("Имя клиента не может быть пустым")
        name = name.strip()
        max_len = self._config.validation.CLIENT_NAME_MAX_LENGTH
        if len(name) > max_len:
            raise ClientValidationError(
                f"Имя клиента не должно превышать {max_len} символов"
            )
        return name

    def validate_email(self, email: str | None) -> str | None:
        if not email or not email.strip():
            return None
        email = email.strip().lower()
        max_len = self._config.validation.EMAIL_MAX_LENGTH
        if len(email) > max_len:
            raise EmailValidationError(f"Email не должен превышать {max_len} символов")
        if not self.EMAIL_REGEX.fullmatch(email):
            raise EmailValidationError("Некорректный формат email")
        return email

    def validate_phone(self, phone: str | None) -> str | None:
        if not phone or not phone.strip():
            return None
        phone = phone.strip()
        if not self.PHONE_REGEX.fullmatch(phone):
            raise ClientValidationError(
                "Некорректный формат телефона. Ожидается +71234567890"
            )
        return phone
