"""Модуль содержит конфигурацию приложения
Модуль загружает переменные окружения через dotenv и предоставляет
централизованное место для хранения всех настроек приложения.
"""
# Config

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class DatabaseConfig:
    host: str = field(default_factory=lambda: os.getenv("DATABASE_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("DATABASE_PORT", "5432")))
    user: str = field(default_factory=lambda: os.getenv("DATABASE_USER", "user"))
    password: str = field(
        default_factory=lambda: os.getenv("DATABASE_PASSWORD", "password")
    )
    name: str = field(default_factory=lambda: os.getenv("DATABASE_NAME", "omnichannel"))
    url: str | None = field(default_factory=lambda: os.getenv("DATABASE_URL"))

    def build_url(self) -> str:
        if self.url:
            raw = self.url
            if raw.startswith("postgresql://"):
                raw = raw.replace("postgresql://", "postgresql+asyncpg://", 1)
            return raw
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class TelegramConfig:
    token: str | None = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN"))


@dataclass
class EmailConfig:
    host: str | None = field(default_factory=lambda: os.getenv("EMAIL_HOST"))
    port: int = field(default_factory=lambda: int(os.getenv("EMAIL_PORT", "993")))
    user: str | None = field(default_factory=lambda: os.getenv("EMAIL_USER"))
    password: str | None = field(default_factory=lambda: os.getenv("EMAIL_PASSWORD"))
    poll_interval: int = field(
        default_factory=lambda: int(os.getenv("EMAIL_POLL_INTERVAL", "60"))
    )
    smtp_host: str | None = field(
        default_factory=lambda: os.getenv("EMAIL_SMTP_HOST") or os.getenv("EMAIL_HOST")
    )
    smtp_port: int = field(
        default_factory=lambda: int(os.getenv("EMAIL_SMTP_PORT", "587"))
    )


@dataclass
class AppConfig:
    debug: bool = field(
        default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true"
    )
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    testing: bool = field(
        default_factory=lambda: os.getenv("TESTING", "false").lower() == "true"
    )
    base_problem_uri: str = field(
        default_factory=lambda: os.getenv(
            "BASE_PROBLEM_URI", "https://errors.omnichannel.local"
        )
    )


@dataclass
class MinIOConfig:
    endpoint: str = field(default_factory=lambda: os.getenv("MINIO_ENDPOINT", ""))
    access_key: str = field(default_factory=lambda: os.getenv("MINIO_ACCESS_KEY", ""))
    secret_key: str = field(default_factory=lambda: os.getenv("MINIO_SECRET_KEY", ""))
    bucket: str = field(default_factory=lambda: os.getenv("MINIO_BUCKET", ""))


@dataclass
class ValidationConfig:
    ALLOWED_UPLOAD_EXTENSIONS: tuple[str, ...] = (
        "jpg",
        "jpeg",
        "png",
        "gif",
        "webp",
        "mp4",
        "webm",
        "pdf",
        "doc",
        "docx",
        "xls",
        "xlsx",
        "txt",
        "csv",
    )
    MAX_FILE_SIZE: int = 50 * 1024 * 1024
    MAX_MESSAGE_LENGTH: int = 10000
    CLIENT_NAME_MAX_LENGTH: int = 255
    EMAIL_MAX_LENGTH: int = 255


@dataclass
class AuthConfig:
    jwt_secret: str = field(
        default_factory=lambda: os.getenv("JWT_SECRET", "change-me")
    )
    jwt_algorithm: str = field(
        default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256")
    )
    access_token_expire_minutes: int = field(
        default_factory=lambda: int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    )


@dataclass
class Config:
    """Класс конфигурации приложения

    Содержит параметры конфигурации, которые используются во всех слоях
    приложения.
    """

    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    email: EmailConfig = field(default_factory=EmailConfig)
    app: AppConfig = field(default_factory=AppConfig)
    minio: MinIOConfig = field(default_factory=MinIOConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)


config = Config()
