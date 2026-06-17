import logging
import asyncio
import io
from typing import AsyncGenerator

from telegram import Bot
from telegram.ext import Application, MessageHandler, filters

from app.core.ports.message_engine import MessageEngine
from app.core.ports.s3 import S3Interface
from app.core.domain.models.message import Message
from app.core.domain.models.channel_type import ChannelType, MessageType

logger = logging.getLogger(__name__)


class TelegramEngine(MessageEngine):
    def __init__(self, token: str, s3: S3Interface | None = None):
        self._token = token
        self._s3 = s3
        self._app: Application = None
        self._running = False
        self._channel_type = ChannelType.TELEGRAM
        self._queue: asyncio.Queue[Message] = asyncio.Queue()

    async def start(self) -> None:
        self._app = Application.builder().token(self._token).build()
        self._app.add_handler(MessageHandler(filters.ALL, self._handle_message))
        await self._app.initialize()
        await self._app.start()
        await self._app.updater.start_polling()
        self._running = True
        logger.info("Telegram engine started")

    async def stop(self) -> None:
        if self._app:
            await self._app.updater.stop()
            await self._app.stop()
            await self._app.shutdown()
        self._running = False
        logger.info("Telegram engine stopped")

    async def send_message(self, recipient: str, content: str, **kwargs) -> str:
        bot = Bot(self._token)
        sent = await bot.send_message(chat_id=recipient, text=content)
        return str(sent.message_id)

    async def get_incoming(self) -> AsyncGenerator[Message, None]:
        while self._running:
            try:
                message = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                yield message
            except asyncio.TimeoutError:
                continue

    @property
    def channel_type(self) -> str:
        return self._channel_type

    @property
    def is_running(self) -> bool:
        return self._running

    async def _handle_message(self, update, context) -> None:
        if not update.message:
            return

        msg = update.message

        content = msg.text or msg.caption or ""

        message_type = MessageType.TEXT
        media_type = None
        file_url = None
        if msg.photo:
            media_type = "photo"
            message_type = MessageType.PHOTO
        elif msg.document:
            media_type = "document"
            message_type = MessageType.DOCUMENT
        elif msg.video:
            media_type = "video"
            message_type = MessageType.VIDEO
        elif msg.audio:
            media_type = "audio"
            message_type = MessageType.AUDIO
        elif msg.voice:
            media_type = "voice"
            message_type = MessageType.VOICE
        elif msg.sticker:
            media_type = "sticker"
            message_type = MessageType.STICKER
            if self._s3:
                try:
                    file = await msg.sticker.get_file()

                    if msg.sticker.is_video:
                        ext = ".webm"
                        content_type = "video/webm"
                    elif msg.sticker.is_animated:
                        ext = ".tgs"
                        content_type = "application/gzip"
                    else:
                        ext = ".webp"
                        content_type = "image/webp"

                    buf = io.BytesIO()
                    await file.download_to_memory(buf)
                    buf.seek(0)

                    object_name = f"stickers/{msg.sticker.file_id}{ext}"
                    self._s3.put_object(
                        object_name=object_name,
                        data=buf,
                        size=buf.getbuffer().nbytes,
                        content_type=content_type,
                    )
                    file_url = self._s3.generate_presigned_url(
                        object_name, expiration=86400
                    )
                except Exception as e:
                    logger.error(f"Failed to upload sticker to S3: {e}")

        if not content and media_type:
            content = f"[{media_type}]"

        metadata: dict = {
            "chat_id": msg.chat_id,
            "message_id": msg.message_id,
            "username": msg.from_user.username,
            "first_name": msg.from_user.first_name,
        }
        if media_type:
            metadata["media_type"] = media_type
        if file_url:
            metadata["file_url"] = file_url

        message = Message(
            id=f"telegram:{msg.message_id}",
            channel=self._channel_type,
            sender_id=str(msg.from_user.id),
            content=content,
            timestamp=msg.date,
            message_type=message_type,
            metadata=metadata,
        )
        logger.info(f"Received message from Telegram: {message.id}")
        await self._queue.put(message)
