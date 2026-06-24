from enum import StrEnum


class ChannelType(StrEnum):
    TELEGRAM = "telegram"
    EMAIL = "email"
    SLACK = "slack"
    DISCORD = "discord"
    VK = "vk"


class MessageType(StrEnum):
    TEXT = "text"
    STICKER = "sticker"
    PHOTO = "photo"
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"
    VOICE = "voice"
    ANIMATION = "animation"


class CuratorRole(StrEnum):
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    AGENT = "agent"


class CuratorStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
