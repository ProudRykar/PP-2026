import logging
import asyncio
import io
import os
from typing import AsyncGenerator, Optional
from urllib.parse import urlparse

import aiohttp
from telegram import Bot, InputFile
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
        self._app: Optional[Application] = None
        self._running = False
        self._channel_type = ChannelType.TELEGRAM
        self._queue: asyncio.Queue[Message] = asyncio.Queue()

    async def start(self) -> None:
        self._app = Application.builder().token(self._token).build()
        self._app.add_handler(MessageHandler(filters.ALL, self._handle_message))
        await self._app.initialize()
        await self._app.start()
        assert self._app is not None and self._app.updater is not None
        await self._app.updater.start_polling()
        self._running = True
        logger.info("Telegram engine started")

    async def stop(self) -> None:
        if self._app is not None and self._app.updater is not None:
            await self._app.updater.stop()
            await self._app.stop()
            await self._app.shutdown()
        self._running = False
        logger.info("Telegram engine stopped")

    async def send_message(self, recipient: str, content: str, **kwargs) -> str:
        bot = Bot(self._token)
        file_url = kwargs.get("file_url") or kwargs.get("photo")
        if file_url:
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as resp:
                    resp.raise_for_status()
                    file_bytes = await resp.read()

            parsed = urlparse(file_url)
            _, ext = os.path.splitext(parsed.path)
            ext = ext.lower()

            if ext in (".gif", ".mp4", ".webm"):
                filename = f"animation{ext}"
                sent = await bot.send_animation(
                    chat_id=recipient,
                    animation=InputFile(file_bytes, filename=filename),
                    caption=content or None,
                )
            elif ext in (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".csv"):
                filename = f"document{ext}"
                sent = await bot.send_document(
                    chat_id=recipient,
                    document=InputFile(file_bytes, filename=filename),
                    caption=content or None,
                )
            else:
                sent = await bot.send_photo(
                    chat_id=recipient,
                    photo=InputFile(file_bytes, filename="photo.jpg"),
                    caption=content or None,
                )
        else:
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

    async def _upload_photo_to_s3(self, msg) -> str | None:
        if not self._s3 or not msg.photo:
            return None
        try:
            best_photo = msg.photo[-1]
            file = await best_photo.get_file()

            buf = io.BytesIO()
            await file.download_to_memory(buf)
            buf.seek(0)

            object_name = f"photos/{file.file_id}.jpg"
            self._s3.put_object(
                object_name=object_name,
                data=buf,
                size=buf.getbuffer().nbytes,
                content_type="image/jpeg",
            )
            return self._s3.generate_presigned_url(object_name, expiration=86400)
        except Exception as e:
            logger.error(f"Failed to upload photo to S3: {e}")
            return None

    async def _upload_sticker_to_s3(self, msg) -> str | None:
        if not self._s3 or not msg.sticker:
            return None
        try:
            file = await msg.sticker.get_file()

            if msg.sticker.is_video:
                ext, content_type = ".webm", "video/webm"
            elif msg.sticker.is_animated:
                ext, content_type = ".tgs", "application/gzip"
            else:
                ext, content_type = ".webp", "image/webp"

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
            return self._s3.generate_presigned_url(object_name, expiration=86400)
        except Exception as e:
            logger.error(f"Failed to upload sticker to S3: {e}")
            return None

    async def _upload_animation_file_to_s3(self, doc) -> str | None:
        if not self._s3:
            return None
        try:
            file = await doc.get_file()
            buf = io.BytesIO()
            await file.download_to_memory(buf)
            buf.seek(0)

            object_name = f"animations/{file.file_id}.gif"
            self._s3.put_object(
                object_name=object_name,
                data=buf,
                size=buf.getbuffer().nbytes,
                content_type="image/gif",
            )
            return self._s3.generate_presigned_url(object_name, expiration=86400)
        except Exception as e:
            logger.error(f"Failed to upload GIF document to S3: {e}")
            return None

    async def _upload_document_to_s3(self, msg) -> str | None:
        if not self._s3 or not msg.document:
            return None
        try:
            doc = msg.document
            file = await doc.get_file()

            file_name = doc.file_name or "document"
            _, ext = os.path.splitext(file_name)
            mime_type = doc.mime_type or "application/octet-stream"

            buf = io.BytesIO()
            await file.download_to_memory(buf)
            buf.seek(0)

            object_name = f"documents/{file.file_id}{ext}"
            self._s3.put_object(
                object_name=object_name,
                data=buf,
                size=buf.getbuffer().nbytes,
                content_type=mime_type,
            )
            return self._s3.generate_presigned_url(object_name, expiration=86400)
        except Exception as e:
            logger.error(f"Failed to upload document to S3: {e}")
            return None

    async def _upload_animation_to_s3(self, msg) -> str | None:
        if not self._s3 or not msg.animation:
            return None
        try:
            animation = msg.animation
            file = await animation.get_file()

            mime_type = animation.mime_type or "video/mp4"
            if mime_type == "image/gif":
                ext, content_type = ".gif", "image/gif"
            else:
                ext, content_type = ".mp4", "video/mp4"

            buf = io.BytesIO()
            await file.download_to_memory(buf)
            buf.seek(0)

            object_name = f"animations/{file.file_id}{ext}"
            self._s3.put_object(
                object_name=object_name,
                data=buf,
                size=buf.getbuffer().nbytes,
                content_type=content_type,
            )
            return self._s3.generate_presigned_url(object_name, expiration=86400)
        except Exception as e:
            logger.error(f"Failed to upload animation to S3: {e}")
            return None

    async def _handle_message(self, update, context) -> None:
        if not update.message:
            return

        msg = update.message
        content = msg.text or msg.caption or ""

        message_type = MessageType.TEXT
        media_type = None
        file_url = None
        mime_type = None
        if msg.animation:
            media_type = "animation"
            message_type = MessageType.ANIMATION
            file_url = await self._upload_animation_to_s3(msg)
            mime_type = msg.animation.mime_type or "video/mp4"
        elif msg.photo:
            media_type = "photo"
            message_type = MessageType.PHOTO
            file_url = await self._upload_photo_to_s3(msg)
        elif msg.sticker:
            media_type = "sticker"
            message_type = MessageType.STICKER
            file_url = await self._upload_sticker_to_s3(msg)
        elif msg.document:
            if msg.document.mime_type == "image/gif":
                media_type = "animation"
                message_type = MessageType.ANIMATION
                file_url = await self._upload_animation_file_to_s3(msg.document)
                mime_type = "image/gif"
            else:
                media_type = "document"
                message_type = MessageType.DOCUMENT
                file_url = await self._upload_document_to_s3(msg)
                mime_type = msg.document.mime_type or "application/octet-stream"
        elif msg.video:
            media_type = "video"
            message_type = MessageType.VIDEO
        elif msg.audio:
            media_type = "audio"
            message_type = MessageType.AUDIO
        elif msg.voice:
            media_type = "voice"
            message_type = MessageType.VOICE

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
        if mime_type:
            metadata["mime_type"] = mime_type
        if media_type == "document" and msg.document:
            metadata["file_name"] = msg.document.file_name or "document"
            metadata["file_size"] = msg.document.file_size or 0

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
