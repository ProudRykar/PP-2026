import logging
import asyncio
import re
from typing import List, Optional

from app.core.ports.message_engine import MessageEngine
from app.core.ports.polling_service import (
    PollingService as AbstractPollingService,
)
from app.core.services.message_service import MessageService
from app.core.services.client_service import ClientService
from app.events import broadcast_message

logger = logging.getLogger(__name__)


class PollingOrchestrator(AbstractPollingService):
    def __init__(self, message_service: MessageService, client_service: ClientService):
        self._message_service = message_service
        self._client_service = client_service
        self._engines: List[MessageEngine] = []
        self._running = False
        self._tasks: List[asyncio.Task] = []

    def register_engine(self, engine: MessageEngine) -> None:
        self._engines.append(engine)
        logger.info(f"Engine registered: {engine.channel_type}")

    async def start_polling(self) -> None:
        self._running = True
        for engine in self._engines:
            try:
                await engine.start()
                task = asyncio.create_task(self._poll_engine(engine))
                self._tasks.append(task)
                logger.info(f"Polling started for {engine.channel_type}")
            except Exception as e:
                logger.error(f"Failed to start {engine.channel_type} engine: {e}")

        logger.info(f"Polling started for {len(self._engines)} engines")

    async def send_reply(
        self,
        channel: str,
        recipient: str,
        content: str,
        subject: str | None = None,
        **kwargs,
    ) -> str | None:
        for engine in self._engines:
            if engine.channel_type == channel:
                try:
                    return await engine.send_message(
                        recipient=recipient,
                        content=content,
                        subject=subject or "",
                        **kwargs,
                    )
                except Exception as e:
                    logger.error(f"Error sending reply via {channel}: {e}")
                    return None
        logger.warning(f"No engine found for channel: {channel}")
        return None

    async def stop_polling(self) -> None:
        self._running = False
        for engine in self._engines:
            try:
                await engine.stop()
            except Exception as e:
                logger.error(f"Error stopping engine {engine.channel_type}: {e}")

        for task in self._tasks:
            task.cancel()

        self._tasks.clear()
        logger.info("Polling stopped")

    def _extract_client_info(
        self, message
    ) -> tuple[str, str, Optional[str], Optional[str]]:
        channel = message.channel
        raw_id = message.sender_id
        external_id = raw_id
        name: Optional[str] = None
        username: Optional[str] = None

        if channel == "telegram":
            username = message.metadata.get("username")
            first_name = message.metadata.get("first_name")
            name = first_name or username or external_id
        elif channel == "email":
            match_email = re.search(r"<([^>]+)>", raw_id)
            if match_email:
                external_id = match_email.group(1)
            match_name = re.match(r'^"?([^"<]+)"?\s*<', raw_id)
            if match_name:
                name = match_name.group(1).strip()
            else:
                name = external_id.split("@")[0] if "@" in external_id else external_id
        else:
            name = external_id

        return channel, external_id, name, username

    async def _poll_engine(self, engine: MessageEngine) -> None:
        try:
            async for message in engine.get_incoming():
                if message:
                    try:
                        channel, external_id, name, username = (
                            self._extract_client_info(message)
                        )
                        avatar_url = (
                            message.metadata.get("file_url")
                            if channel == "telegram"
                            and message.metadata.get("media_type") == "photo"
                            else None
                        )
                        await self._client_service.get_or_create_client(
                            channel=channel,
                            external_id=external_id,
                            name=name,
                            avatar_url=avatar_url,
                            username=username,
                            display_name=name,
                        )

                        await self._message_service.save_message(message)
                        await broadcast_message(
                            {"type": "new_message", **message.to_dict()}
                        )
                        logger.debug(f"Message from {engine.channel_type} saved")
                    except Exception as e:
                        logger.error(
                            f"Error saving message from {engine.channel_type}: {e}"
                        )
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error polling {engine.channel_type}: {e}")
        finally:
            try:
                if engine.is_running:
                    await engine.stop()
            except Exception as e:
                logger.error(f"Error stopping {engine.channel_type}: {e}")
