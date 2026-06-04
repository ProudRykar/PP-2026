import logging

from litestar import Controller, get, post
from litestar.exceptions import HTTPException
from litestar.params import Parameter
from litestar.status_codes import HTTP_404_NOT_FOUND

from app.api.schemas.message_dto import ReplyRequest
from app.adapters.interfaces.polling_service import PollingService
from app.core.domain.models.channel_type import ChannelType
from app.core.errors.message import MessageNotFoundError
from app.core.services.message_service import MessageService

logger = logging.getLogger(__name__)


class MessageController(Controller):
    path = "/api"

    @get("/messages")
    async def get_messages(
        self,
        service: MessageService,
        channel: str | None = Parameter(
            default=None, description="Filter by channel type"
        ),
        limit: int = Parameter(default=100, ge=1, le=1000),
        offset: int = Parameter(default=0, ge=0),
    ) -> list[dict]:
        messages = await service.get_messages(
            channel=channel, limit=limit, offset=offset
        )
        return [msg.to_dict() for msg in messages]

    @get("/messages/{message_id:str}")
    async def get_message(
        self,
        message_id: str,
        service: MessageService,
    ) -> dict:
        message = await service.get_message(message_id)
        if not message:
            raise HTTPException(
                detail="Message not found", status_code=HTTP_404_NOT_FOUND
            )
        return message.to_dict()

    @post("/messages/reply", status_code=200)
    async def reply_to_message(
        self,
        service: MessageService,
        polling: PollingService,
        data: ReplyRequest,
    ) -> dict:
        try:
            original = await service.reply_to_message(data.message_id, data.content)
        except MessageNotFoundError as e:
            raise HTTPException(detail=str(e), status_code=HTTP_404_NOT_FOUND)

        await polling.send_reply(original.channel, original.sender, data.content)
        return {"status": "success", "message": "Reply sent"}

    @get("/channels")
    async def get_channels(self) -> dict:
        return {
            "channels": [
                ChannelType.TELEGRAM,
                ChannelType.EMAIL,
            ]
        }
