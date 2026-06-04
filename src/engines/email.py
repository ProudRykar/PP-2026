import logging
import imaplib
import email
from email.header import decode_header
from typing import AsyncGenerator, Optional
from datetime import datetime
from src.core.interfaces import MessageEngine
from src.core.models import Message, ChannelType

logger = logging.getLogger(__name__)


class EmailEngine(MessageEngine):
    """Простой движок для получения сообщений по email через IMAP"""

    def __init__(self, host: str, port: int, user: str, password: str, poll_interval: int = 60, repository=None):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._poll_interval = poll_interval
        self._running = False
        self._channel_type = ChannelType.EMAIL
        self._repository = repository
        self._task = None

    async def start(self) -> None:
        """Начать опрос почтового ящика"""
        self._running = True
        import asyncio
        self._task = asyncio.create_task(self._poll_loop())
        logger.info("Движок Email запущен")

    async def stop(self) -> None:
        """Прекратить опрос почтового ящика"""
        self._running = False
        if self._task:
            self._task.cancel()
        logger.info("Движок Email остановлен")

    async def send_message(self, recipient: str, content: str, **kwargs) -> str:
        """Отправить сообзение по email (не реализовано)"""
        raise NotImplementedError("Отправка email через SMTP не реализована в этом движке")

    async def get_incoming(self) -> AsyncGenerator[Message, None]:
        """Получить входящие сообщения"""
        if False:  # Делает это генератором
            yield

    @property
    def channel_type(self) -> str:
        return self._channel_type

    @property
    def is_running(self) -> bool:
        return self._running

    def _decode_header_value(self, value: str) -> str:
        """Декодировать заголовок email, который может быть в кодировке MIME"""
        if not value:
            return ""
        decoded_parts = decode_header(value)
        result = []
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                result.append(part.decode(charset or 'utf-8', errors='ignore'))
            else:
                result.append(str(part))
        return ' '.join(result)

    async def _poll_loop(self) -> None:
        """Основной цикл опроса почтового ящика на наличие новых сообщений"""
        import asyncio
        
        while self._running:
            try:
                messages = await self._fetch_new_messages()
                for msg in messages:
                    if self._repository:
                        try:
                            await self._repository.save_message(msg)
                            logger.info(f"Сохранено сообщение email: {msg.id}")
                        except Exception as e:
                            logger.error(f"Ошибка при сохранении email: {e}")
            except Exception as e:
                logger.error(f"Ошибка опроса email: {e}")

            await asyncio.sleep(self._poll_interval)

    async def _fetch_new_messages(self) -> list:
        """Метод для получения новых сообщений из почтового ящика"""
        import asyncio
        messages = []

        try:
            loop = asyncio.get_event_loop()
            mail = await loop.run_in_executor(
                None,
                lambda: imaplib.IMAP4_SSL(self._host, self._port)
            )
            await loop.run_in_executor(None, lambda: mail.login(self._user, self._password))
            await loop.run_in_executor(None, lambda: mail.select('inbox'))

            status, messages_data = await loop.run_in_executor(
                None, lambda: mail.search(None, 'ALL')
            )

            if status == 'OK':
                email_ids = messages_data[0].split()
                # Получить последние 10 сообщений
                for email_id in email_ids[-10:]:
                    status, msg_data = await loop.run_in_executor(
                        None, lambda: mail.fetch(email_id, '(RFC822)')
                    )
                    if status == 'OK':
                        raw_email = msg_data[0][1]
                        msg = email.message_from_bytes(raw_email)

                        subject = self._decode_header_value(msg.get('Subject', ''))
                        from_addr = self._decode_header_value(msg.get('From', ''))
                        date = msg.get('Date')

                        content = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    payload = part.get_payload(decode=True)
                                    if payload:
                                        content = payload.decode('utf-8', errors='ignore')
                                        break
                        else:
                            payload = msg.get_payload(decode=True)
                            if payload:
                                content = payload.decode('utf-8', errors='ignore')

                        message = Message(
                            id=f"email:{datetime.now().timestamp()}:{email_id.decode()}",
                            channel=self._channel_type,
                            sender=from_addr,
                            content=content,
                            timestamp=datetime.now(),
                            metadata={
                                "subject": subject,
                                "email_id": email_id.decode(),
                                "date": date or "",
                            },
                            recipient=self._user,
                            subject=subject
                        )
                        messages.append(message)

            await loop.run_in_executor(None, lambda: mail.logout())

        except Exception as e:
            logger.error(f"Ошибка IMAP: {e}")

        return messages
