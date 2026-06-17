import logging
import asyncio
import imaplib
import smtplib
import ssl
import email
import re
from email.message import EmailMessage
from email.header import decode_header
from typing import AsyncGenerator
from datetime import datetime

from app.core.ports.message_engine import MessageEngine
from app.core.domain.models.message import Message
from app.core.domain.models.channel_type import ChannelType, MessageType

logger = logging.getLogger(__name__)


class EmailEngine(MessageEngine):
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        poll_interval: int = 60,
        smtp_host: str | None = None,
        smtp_port: int = 587,
    ):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._poll_interval = poll_interval
        self._smtp_host = smtp_host or host
        self._smtp_port = smtp_port
        self._running = False
        self._channel_type = ChannelType.EMAIL

    async def start(self) -> None:
        self._running = True
        logger.info("Email engine started")

    async def stop(self) -> None:
        self._running = False
        logger.info("Email engine stopped")

    @staticmethod
    def _extract_email(address: str) -> str:
        match = re.search(r"<([^>]+)>", address)
        return match.group(1) if match else address.strip()

    async def send_message(self, recipient: str, content: str, **kwargs) -> str:
        subject = kwargs.get("subject", "")
        to_addr = self._extract_email(recipient)
        logger.info("Sending email via SMTP to %s (subject: %s)", to_addr, subject)

        def _send() -> str:
            msg = EmailMessage()
            msg["From"] = self._user
            msg["To"] = to_addr
            msg["Subject"] = subject
            msg.set_content(content)

            try:
                if self._smtp_port == 465:
                    ctx = ssl.create_default_context()
                    with smtplib.SMTP_SSL(
                        self._smtp_host, self._smtp_port, timeout=10, context=ctx
                    ) as server:
                        server.login(self._user, self._password)
                        server.send_message(msg)
                else:
                    with smtplib.SMTP(
                        self._smtp_host, self._smtp_port, timeout=10
                    ) as server:
                        server.starttls()
                        server.login(self._user, self._password)
                        server.send_message(msg)
            except smtplib.SMTPAuthenticationError:
                logger.error("SMTP auth failed for %s", self._user)
                raise
            except OSError as e:
                logger.error(
                    "SMTP connection error to %s:%s: %s",
                    self._smtp_host,
                    self._smtp_port,
                    e,
                )
                raise

            logger.info("Email sent successfully to %s", to_addr)
            return f"sent:{to_addr}"

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _send)

    async def get_incoming(self) -> AsyncGenerator[Message, None]:
        while self._running:
            try:
                messages = await self._fetch_new_messages()
                for msg in messages:
                    yield msg
            except Exception as e:
                logger.error(f"Error polling email: {e}")
            await asyncio.sleep(self._poll_interval)

    @property
    def channel_type(self) -> str:
        return self._channel_type

    @property
    def is_running(self) -> bool:
        return self._running

    def _decode_header_value(self, value: str) -> str:
        if not value:
            return ""
        decoded_parts = decode_header(value)
        result = []
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                result.append(part.decode(charset or "utf-8", errors="ignore"))
            else:
                result.append(str(part))
        return " ".join(result)

    def _extract_body(self, msg) -> tuple[str, str]:
        if msg.is_multipart():
            text_content = ""
            html_content = ""
            for part in msg.walk():
                ctype = part.get_content_type()
                payload = part.get_payload(decode=True)
                if not isinstance(payload, bytes):
                    continue
                if ctype == "text/plain":
                    decoded = payload.decode("utf-8", errors="ignore")
                    if decoded.strip():
                        text_content = decoded
                elif ctype == "text/html":
                    html_content = payload.decode("utf-8", errors="ignore")
            if html_content:
                return text_content or "", html_content
            return text_content, ""
        payload = msg.get_payload(decode=True)
        if not isinstance(payload, bytes):
            return "", ""
        content = payload.decode("utf-8", errors="ignore")
        ctype = msg.get_content_type() or ""
        if "html" in ctype.lower():
            return "", content
        return content, ""

    async def _fetch_new_messages(self) -> list:
        messages: list = []

        if not self._user or not self._password:
            logger.warning("Email credentials not configured, skipping fetch")
            return messages

        try:
            loop = asyncio.get_event_loop()
            mail = await loop.run_in_executor(
                None, lambda: imaplib.IMAP4_SSL(self._host, self._port)
            )
            user_enc = self._user.encode("ascii", errors="ignore").decode("ascii")
            pass_enc = self._password.encode("ascii", errors="ignore").decode("ascii")
            await loop.run_in_executor(None, lambda: mail.login(user_enc, pass_enc))
            await loop.run_in_executor(None, lambda: mail.select("inbox"))

            status, messages_data = await loop.run_in_executor(
                None, lambda: mail.search(None, "ALL")
            )

            if status == "OK":
                raw_ids = messages_data[0]
                email_ids: list[bytes] = (
                    raw_ids.split() if isinstance(raw_ids, bytes) else []
                )
                for email_id_bytes in email_ids[-10:]:
                    email_id_str = email_id_bytes.decode()
                    status, msg_data = await loop.run_in_executor(
                        None, lambda: mail.fetch(email_id_str, "(RFC822)")
                    )
                    if status == "OK":
                        raw_item = msg_data[0]
                        if isinstance(raw_item, tuple) and len(raw_item) > 1:
                            raw_bytes = raw_item[1]
                        else:
                            continue
                        raw_email = (
                            raw_bytes
                            if isinstance(raw_bytes, bytes)
                            else bytes(raw_bytes)
                        )  # type: ignore[arg-type]
                        msg = email.message_from_bytes(raw_email)

                        subject = self._decode_header_value(str(msg.get("Subject", "")))
                        from_addr = self._decode_header_value(str(msg.get("From", "")))
                        date = msg.get("Date")

                        text_body, html_body = self._extract_body(msg)
                        content = html_body if html_body else text_body

                        message = Message(
                            id=f"email:{datetime.now().timestamp()}:{email_id_bytes.decode()}",
                            channel=self._channel_type,
                            sender_id=from_addr,
                            content=content,
                            timestamp=datetime.now(),
                            message_type=MessageType.TEXT,
                            metadata={
                                "subject": subject,
                                "email_id": email_id_bytes.decode(),
                                "date": date or "",
                                "has_html": bool(html_body),
                                "text_preview": text_body[:500] if text_body else "",
                            },
                            recipient=self._user,
                            subject=subject,
                        )
                        messages.append(message)

            await loop.run_in_executor(None, lambda: mail.logout())

        except Exception as e:
            logger.error(f"IMAP error: {e}")

        return messages
