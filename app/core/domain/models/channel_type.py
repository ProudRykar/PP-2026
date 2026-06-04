from enum import StrEnum


class ChannelType(StrEnum):
    TELEGRAM = "telegram"
    EMAIL = "email"
    SLACK = "slack"
    DISCORD = "discord"
    VK = "vk"
