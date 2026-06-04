import logging
import asyncio
from typing import List
from src.core.interfaces import PollingService, MessageEngine
from src.services.message_service import MessageService

logger = logging.getLogger(__name__)


class PollingService(PollingService):
    """Сервис для управления циклом опроса всех зарегистрированных движков сообщений"""

    def __init__(
        self,
        message_service: MessageService,
        engines: List[MessageEngine] = None
    ):
        self._message_service = message_service
        self._engines: List[MessageEngine] = engines or []
        self._running = False
        self._tasks: List[asyncio.Task] = []

    def register_engine(self, engine: MessageEngine) -> None:
        """Зарегистрировать движок для опроса"""
        self._engines.append(engine)
        logger.info(f"Зарегистрирован движок: {engine.channel_type}")

    async def start_polling(self) -> None:
        """Начать опрос всех зарегистрированных движков"""
        self._running = True

        for engine in self._engines:
            await engine.start()
            task = asyncio.create_task(self._poll_engine(engine))
            self._tasks.append(task)
            logger.info(f"Опрос движка {engine.channel_type} запущен")

        logger.info(f"Опрос запущен для {len(self._engines)} движков")

    async def stop_polling(self) -> None:
        """Остановить опрос всех движков и очистить ресурсы"""
        self._running = False

        for engine in self._engines:
            try:
                await engine.stop()
            except Exception as e:
                logger.error(f"Ошибка при остановке движка {engine.channel_type}: {e}")

        for task in self._tasks:
            task.cancel()

        self._tasks.clear()
        logger.info("Опрос остановлен")

    async def _poll_engine(self, engine: MessageEngine) -> None:
        """Опросить один движок для получения сообщений"""
        try:
            await engine.start()
            logger.info(f"Движок {engine.channel_type} успешно запущен")
            
            async for message in engine.get_incoming():
                if message:
                    try:
                        await self._message_service.save_message(message)
                        logger.debug(f"Сообщение от {engine.channel_type} сохранено")
                    except Exception as e:
                        logger.error(f"Ошибка сохранения сообщения от {engine.channel_type}: {e}")
        except Exception as e:
            logger.error(f"Ошибка опроса {engine.channel_type}: {e}")
        finally:
            try:
                if engine.is_running:
                    await engine.stop()
            except Exception as e:
                logger.error(f"Ошибка остановки {engine.channel_type}: {e}")
