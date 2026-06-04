import logging
import asyncio
from typing import List

from app.core.ports.message_engine import MessageEngine
from app.core.ports.polling_service import (
    PollingService as AbstractPollingService,
)
from app.core.services.message_service import MessageService
from app.events import broadcast_message

logger = logging.getLogger(__name__)


class PollingOrchestrator(AbstractPollingService):
    def __init__(self, message_service: MessageService):
        self._message_service = message_service
        self._engines: List[MessageEngine] = []
        self._running = False
        self._tasks: List[asyncio.Task] = []

    def register_engine(self, engine: MessageEngine) -> None:
        self._engines.append(engine)
        logger.info(f"Engine registered: {engine.channel_type}")

    async def start_polling(self) -> None:
        self._running = True
        for engine in self._engines:
            await engine.start()
            task = asyncio.create_task(self._poll_engine(engine))
            self._tasks.append(task)
            logger.info(f"Polling started for {engine.channel_type}")

        logger.info(f"Polling started for {len(self._engines)} engines")

    async def send_reply(
        self, channel: str, recipient: str, content: str, subject: str | None = None
    ) -> str | None:
        for engine in self._engines:
            if engine.channel_type == channel:
                try:
                    return await engine.send_message(
                        recipient=recipient, content=content, subject=subject or ""
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

    async def _poll_engine(self, engine: MessageEngine) -> None:
        try:
            async for message in engine.get_incoming():
                if message:
                    try:
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
