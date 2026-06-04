import logging
from typing import AsyncGenerator
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, ContextTypes, filters
from src.core.interfaces import MessageEngine
from src.core.models import Message, ChannelType
from datetime import datetime

logger = logging.getLogger(__name__)


class TelegramEngine(MessageEngine):
    """Движок Telegram-бота на базе python-telegram-bot"""

    def __init__(self, token: str, repository=None):
        self._token = token
        self._app: Application = None
        self._running = False
        self._channel_type = ChannelType.TELEGRAM
        self._repository = repository
        self._queue = None

    async def start(self) -> None:
        """Запустить Telegram-бот в режиме polling"""
        self._app = Application.builder().token(self._token).build()
        self._app.add_handler(
            MessageHandler(filters.ALL, self._handle_message)
        )
        await self._app.initialize()
        await self._app.start()
        await self._app.updater.start_polling()
        self._running = True
        logger.info("Движок Telegram запущен")

    async def stop(self) -> None:
        """Остановить Telegram-бот"""
        if self._app:
            await self._app.updater.stop()
            await self._app.stop()
            await self._app.shutdown()
        self._running = False
        logger.info("Движок Telegram остановлен")

    async def send_message(self, recipient: str, content: str, **kwargs) -> str:
        """Отправить сообщение через Telegram-бот"""
        bot = Bot(self._token)
        sent = await bot.send_message(chat_id=recipient, text=content)
        return str(sent.message_id)

    async def get_incoming(self) -> AsyncGenerator[Message, None]:
        """Входящие сообщения обрабатываются через handlers (обработчики)"""
        if False:
            yield

    @property
    def channel_type(self) -> str:
        return self._channel_type

    @property
    def is_running(self) -> bool:
        return self._running

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Внутренний обработчик входящих сообщений"""
        if not update.message:
            return

        msg = update.message
        message = Message(
            id=f"telegram:{msg.message_id}",
            channel=self._channel_type,
            sender=str(msg.from_user.id),
            content=msg.text or "",
            timestamp=msg.date,
            metadata={
                "chat_id": msg.chat_id,
                "message_id": msg.message_id,
                "username": msg.from_user.username,
                "first_name": msg.from_user.first_name,
            }
        )
        logger.info(f"Получено сообщение от Telegram: {message.id}")

        # Сохранить напрямую в БД
        if self._repository:
            try:
                await self._repository.save_message(message)
            except Exception as e:
                logger.error(f"Ошибка при сохранении сообщения от Telegram: {e}")
