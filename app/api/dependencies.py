from app.core.services.message_service import MessageService
from app.container import get_container


def get_message_service() -> MessageService:
    container = get_container()
    return container.resolve(MessageService)
