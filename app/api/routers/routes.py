import base64
import io
import logging
import os
import uuid
from datetime import datetime, timezone

from litestar import Controller, get, post
from litestar.enums import MediaType
from litestar.params import Parameter

from app.api.schemas.message_dto import MessageResponse, ReplyRequest
from app.core.ports.polling_service import PollingService
from app.core.ports.s3 import S3Interface
from app.core.domain.models.channel_type import ChannelType, MessageType
from app.core.domain.models.message import Message
from app.core.errors.message import MessageNotFoundError
from app.core.services.message_service import MessageService
from app.events import broadcast_message
from app.container import get_container

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
        parent_id=msg.parent_id,
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
            raise MessageNotFoundError(message_id)
        return _to_response(message)

    @post("/upload", media_type=MediaType.JSON)
    async def upload_file(
        self,
        data: dict,
    ) -> dict:
        try:
            s3 = get_container().resolve(S3Interface)
        except Exception:
            return {"status": "error", "detail": "S3 storage not configured"}

        file_data = data.get("file")
        filename = data.get("filename", "file.bin")
        if not file_data:
            return {"status": "error", "detail": "No file data provided"}

        raw = base64.b64decode(file_data)

        _, ext = os.path.splitext(filename)
        content_type = data.get("content_type", "application/octet-stream")
        object_name = f"uploads/{uuid.uuid4().hex}{ext}"

        buf = io.BytesIO(raw)
        s3.put_object(
            object_name=object_name,
            data=buf,
            size=buf.getbuffer().nbytes,
            content_type=content_type,
        )
        file_url = s3.generate_presigned_url(object_name, expiration=86400)

        return {"status": "success", "file_url": file_url}

    @post("/messages/reply", status_code=200)
    async def reply_to_message(
        self,
        service: MessageService,
        polling: PollingService,
        data: ReplyRequest,
    ) -> dict:
        original = await service.reply_to_message(data.message_id, data.content)

        reply_subject = (
            data.subject or f"Re: {original.subject}" if original.subject else None
        )

        metadata: dict = {
            "has_html": False,
            "text_preview": data.content[:500] if data.content else "",
            "is_reply": True,
            "subject": reply_subject or "",
        }
        message_type = "text"
        if data.file_url:
            metadata["file_url"] = data.file_url
            message_type = "photo"

        real_recipient = (
            original.recipient or original.sender_id
            if original.sender_id == "agent"
            else original.sender_id
        )

        reply = Message(
            id=f"reply:{uuid.uuid4().hex}",
            channel=original.channel,
            sender_id="agent",
            content=data.content,
            timestamp=datetime.now(timezone.utc),
            metadata=metadata,
            recipient=real_recipient,
            subject=reply_subject,
            message_type=MessageType(message_type),
            parent_id=data.message_id,
        )
        await service.save_message(reply)
        await broadcast_message({"type": "new_message", **reply.to_dict()})
        await polling.send_reply(
            original.channel,
            real_recipient,
            data.content,
            subject=reply_subject,
            file_url=data.file_url,
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
