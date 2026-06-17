import logging

from datetime import datetime, timezone

from litestar import Controller, get, post
from litestar.exceptions import HTTPException
from litestar.params import Parameter
from litestar.status_codes import HTTP_404_NOT_FOUND

from app.api.schemas.message_dto import MessageResponse, ReplyRequest
from app.core.ports.polling_service import PollingService
from app.core.domain.models.channel_type import ChannelType
from app.core.domain.models.message import Message
from app.core.errors.message import MessageNotFoundError
from app.core.services.message_service import MessageService
from app.events import broadcast_message

logger = logging.getLogger(__name__)


def _to_response(msg: Message) -> MessageResponse:
    return MessageResponse(
        id=msg.id,
        channel=msg.channel,
        sender_id=msg.sender_id,
        content=msg.content,
        timestamp=msg.timestamp,
        message_type=msg.message_type.value,
        metadata=msg.metadata,
        recipient=msg.recipient,
        subject=msg.subject,
    )


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
    ) -> list[MessageResponse]:
        messages = await service.get_messages(
            channel=channel, limit=limit, offset=offset
        )
        return [_to_response(msg) for msg in messages]

    @get("/messages/{message_id:str}")
    async def get_message(
        self,
        message_id: str,
        service: MessageService,
    ) -> MessageResponse:
        message = await service.get_message(message_id)
        if not message:
            raise HTTPException(
                detail="Message not found", status_code=HTTP_404_NOT_FOUND
            )
        return _to_response(message)

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

        reply_subject = (
            data.subject or f"Re: {original.subject}" if original.subject else None
        )
        reply = Message(
            id=f"reply:{data.message_id}:{datetime.now(timezone.utc).timestamp()}",
            channel=original.channel,
            sender_id="agent",
            content=data.content,
            timestamp=datetime.now(timezone.utc),
            metadata={
                "has_html": False,
                "text_preview": data.content[:500] if data.content else "",
                "is_reply": True,
                "subject": reply_subject or "",
            },
            recipient=original.sender_id,
            subject=reply_subject,
        )
        await service.save_message(reply)
        await broadcast_message({"type": "new_message", **reply.to_dict()})
        await polling.send_reply(
            original.channel, original.sender_id, data.content, subject=reply_subject
        )
        return {"status": "success", "message": "Reply sent"}

    @get("/channels")
    async def get_channels(self) -> dict:
        return {
            "channels": [
                ChannelType.TELEGRAM,
                ChannelType.EMAIL,
            ]
        }
