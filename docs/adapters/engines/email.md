## Класс EmailEngine


```python
class EmailEngine(MessageEngine):
```

---
## def init:

```python
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        poll_interval: int = 60,
    ):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._poll_interval = poll_interval
        self._running = False
        self._channel_type = ChannelType.EMAIL
```
---
## async def start:

```python
    async def start(self) -> None:
        self._running = True
        logger.info("Email engine started")
```
---
## async def stop:

```python
    async def stop(self) -> None:
        self._running = False
        logger.info("Email engine stopped")
```
---
## async def send_message:

```python
    async def send_message(self, recipient: str, content: str, **kwargs) -> str:
        raise NotImplementedError(
            "Email sending via SMTP is not implemented"
        )
```
---
## async def get_incoming:

```python
    async def get_incoming(self) -> AsyncGenerator[Message, None]:
        while self._running:
            try:
                messages = await self._fetch_new_messages()
                for msg in messages:
                    yield msg
            except Exception as e:
                logger.error(f"Error polling email: {e}")
            await asyncio.sleep(self._poll_interval)
```
---
## def channel_type:

```python
    @property
    def channel_type(self) -> str:
        return self._channel_type
```
---
## def is_running:

```python
    @property
    def is_running(self) -> bool:
        return self._running
```
---
## def _decode_header_value:

```python
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
```
---
## async def _fetch_new_messages:

```python
    async def _fetch_new_messages(self) -> list:
        messages = []

        try:
            loop = asyncio.get_event_loop()
            mail = await loop.run_in_executor(
                None, lambda: imaplib.IMAP4_SSL(self._host, self._port)
            )
            await loop.run_in_executor(
                None, lambda: mail.login(self._user, self._password)
            )
            await loop.run_in_executor(None, lambda: mail.select("inbox"))

            status, messages_data = await loop.run_in_executor(
                None, lambda: mail.search(None, "ALL")
            )

            if status == "OK":
                raw_ids = messages_data[0]
                email_ids: list[bytes] = raw_ids.split() if isinstance(raw_ids, bytes) else []
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
                        raw_email = raw_bytes if isinstance(raw_bytes, bytes) else bytes(raw_bytes)  # type: ignore[arg-type]
                        msg = email.message_from_bytes(raw_email)

                        subject = self._decode_header_value(str(msg.get("Subject", "")))
                        from_addr = self._decode_header_value(str(msg.get("From", "")))
                        date = msg.get("Date")

                        content = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    payload = part.get_payload(decode=True)
                                    if isinstance(payload, bytes):
                                        content = payload.decode(
                                            "utf-8", errors="ignore"
                                        )
                                        break
                        else:
                            payload = msg.get_payload(decode=True)
                            if isinstance(payload, bytes):
                                content = payload.decode("utf-8", errors="ignore")

                        message = Message(
                            id=f"email:{datetime.now().timestamp()}:{email_id_bytes.decode()}",
                            channel=self._channel_type,
                            sender=from_addr,
                            content=content,
                            timestamp=datetime.now(),
                            metadata={
                                "subject": subject,
                                "email_id": email_id_bytes.decode(),
                                "date": date or "",
                            },
                            recipient=self._user,
                            subject=subject,
                        )
                        messages.append(message)

            await loop.run_in_executor(None, lambda: mail.logout())

        except Exception as e:
            logger.error(f"IMAP error: {e}")

        return messages
```
---