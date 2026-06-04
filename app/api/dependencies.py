from app.core.ports.polling_service import PollingService
from app.core.services.message_service import MessageService
from app.container import get_container


def get_message_service() -> MessageService:
    container = get_container()
    return container.resolve(MessageService)


def get_polling_service() -> PollingService:
    container = get_container()
    return container.resolve(PollingService)
