import pytest

from app.core.errors.validation import (
    ClientValidationError,
    EmailValidationError,
    FileExtensionValidationError,
    FileSizeValidationError,
    FileValidationError,
    MessageValidationError,
)
from app.core.services.validation_service import (
    ClientValidator,
    FileValidator,
    MessageValidator,
)


@pytest.fixture
def file_validator() -> FileValidator:
    return FileValidator()


@pytest.fixture
def message_validator() -> MessageValidator:
    return MessageValidator()


@pytest.fixture
def client_validator() -> ClientValidator:
    return ClientValidator()


class TestFileValidator:
    def test_valid_jpeg(self, file_validator: FileValidator):
        ext = file_validator.validate_file("photo.jpg", "image/jpeg", b"mock_data")
        assert ext == "jpg"

    def test_valid_png(self, file_validator: FileValidator):
        ext = file_validator.validate_file("image.png", "image/png", b"mock_data")
        assert ext == "png"

    def test_valid_gif(self, file_validator: FileValidator):
        ext = file_validator.validate_file("anim.gif", "image/gif", b"mock_data")
        assert ext == "gif"

    def test_valid_mp4(self, file_validator: FileValidator):
        ext = file_validator.validate_file("video.mp4", "video/mp4", b"mock_data")
        assert ext == "mp4"

    def test_valid_webm(self, file_validator: FileValidator):
        ext = file_validator.validate_file("clip.webm", "video/webm", b"mock_data")
        assert ext == "webm"

    def test_empty_filename(self, file_validator: FileValidator):
        with pytest.raises(FileValidationError, match="не может быть пустым"):
            file_validator.validate_file("", "image/jpeg", b"data")

    def test_no_extension(self, file_validator: FileValidator):
        with pytest.raises(FileValidationError, match="должен иметь расширение"):
            file_validator.validate_file("noext", "image/jpeg", b"data")

    def test_bad_extension(self, file_validator: FileValidator):
        with pytest.raises(
            FileExtensionValidationError, match="Недопустимое расширение"
        ):
            file_validator.validate_file(
                "malware.exe", "application/x-msdownload", b"data"
            )

    def test_bad_extension_svg(self, file_validator: FileValidator):
        with pytest.raises(
            FileExtensionValidationError, match="Недопустимое расширение"
        ):
            file_validator.validate_file("vector.svg", "image/svg+xml", b"data")

    def test_file_too_large(self, file_validator: FileValidator):
        big_data = b"x" * (50 * 1024 * 1024 + 1)
        with pytest.raises(
            FileSizeValidationError, match="превышает максимальный размер"
        ):
            file_validator.validate_file("big.jpg", "image/jpeg", big_data)

    def test_uppercase_extension(self, file_validator: FileValidator):
        ext = file_validator.validate_file("photo.JPG", "image/jpeg", b"data")
        assert ext == "jpg"

    def test_empty_data_not_rejected_by_extension_check(
        self, file_validator: FileValidator
    ):
        ext = file_validator.validate_file("empty.gif", "image/gif", b"")
        assert ext == "gif"

    def test_webp_allowed(self, file_validator: FileValidator):
        ext = file_validator.validate_file("sticker.webp", "image/webp", b"data")
        assert ext == "webp"

    def test_with_application_octet_stream(self, file_validator: FileValidator):
        ext = file_validator.validate_file(
            "img.jpg", "application/octet-stream", b"data"
        )
        assert ext == "jpg"


class TestMessageValidator:
    def test_valid_content(self, message_validator: MessageValidator):
        result = message_validator.validate_content("hello")
        assert result == "hello"

    def test_empty_content(self, message_validator: MessageValidator):
        with pytest.raises(MessageValidationError, match="не может быть пустым"):
            message_validator.validate_content("")

    def test_none_content(self, message_validator: MessageValidator):
        with pytest.raises(MessageValidationError, match="не может быть пустым"):
            message_validator.validate_content(None)

    def test_whitespace_content(self, message_validator: MessageValidator):
        with pytest.raises(MessageValidationError, match="не может быть пустым"):
            message_validator.validate_content("   ")

    def test_content_stripped(self, message_validator: MessageValidator):
        result = message_validator.validate_content("  hello  ")
        assert result == "hello"


class TestClientValidator:
    def test_valid_name(self, client_validator: ClientValidator):
        result = client_validator.validate_name("John Doe")
        assert result == "John Doe"

    def test_empty_name(self, client_validator: ClientValidator):
        with pytest.raises(ClientValidationError, match="не может быть пустым"):
            client_validator.validate_name("")

    def test_none_name(self, client_validator: ClientValidator):
        with pytest.raises(ClientValidationError, match="не может быть пустым"):
            client_validator.validate_name(None)

    def test_valid_email(self, client_validator: ClientValidator):
        result = client_validator.validate_email("user@example.com")
        assert result == "user@example.com"

    def test_none_email(self, client_validator: ClientValidator):
        result = client_validator.validate_email(None)
        assert result is None

    def test_empty_email(self, client_validator: ClientValidator):
        result = client_validator.validate_email("")
        assert result is None

    def test_invalid_email(self, client_validator: ClientValidator):
        with pytest.raises(EmailValidationError, match="Некорректный формат email"):
            client_validator.validate_email("not-an-email")

    def test_valid_phone(self, client_validator: ClientValidator):
        result = client_validator.validate_phone("+71234567890")
        assert result == "+71234567890"

    def test_none_phone(self, client_validator: ClientValidator):
        result = client_validator.validate_phone(None)
        assert result is None

    def test_invalid_phone(self, client_validator: ClientValidator):
        with pytest.raises(ClientValidationError, match="Некорректный формат"):
            client_validator.validate_phone("abc")
