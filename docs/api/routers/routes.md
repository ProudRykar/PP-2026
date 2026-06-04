## Класс MessageController


```python
class MessageController(Controller):
    path = "/api"
```

---
## def get_messages:
#### Маршрут:
- **Декоратор:** @get
- **Маршрут:** `/messages`


```python
    @get("/messages")
    async def get_messages(
        self,
        service: MessageService,
        channel: str | None = Parameter(default=None, description="Filter by channel type"),
        limit: int = Parameter(default=100, ge=1, le=1000),
        offset: int = Parameter(default=0, ge=0),
    ) -> list[dict]:
        messages = await service.get_messages(channel=channel, limit=limit, offset=offset)
        return [msg.to_dict() for msg in messages]
```
---
## def get_message:
#### Маршрут:
- **Декоратор:** @get
- **Маршрут:** `/messages/{message_id:str}`


```python
    @get("/messages/{message_id:str}")
    async def get_message(
        self,
        service: MessageService,
        message_id: str,
    ) -> dict:
        message = await service.get_message(message_id)
        if not message:
            raise HTTPException(detail="Message not found", status_code=HTTP_404_NOT_FOUND)
        return message.to_dict()
```
---
## def reply_to_message:
#### Маршрут:
- **Декоратор:** @post
- **Маршрут:** `/messages/reply`


```python
    @post("/messages/reply")
    async def reply_to_message(
        self,
        service: MessageService,
        data: ReplyRequest,
    ) -> dict:
        try:
            await service.reply_to_message(data.message_id, data.content)
        except MessageNotFoundError as e:
            raise HTTPException(detail=str(e), status_code=HTTP_404_NOT_FOUND)
        return {"status": "success", "message": "Reply sent"}
```
---
## def get_channels:
#### Маршрут:
- **Декоратор:** @get
- **Маршрут:** `/channels`


```python
    @get("/channels")
    async def get_channels(self) -> dict:
        return {
            "channels": [
                ChannelType.TELEGRAM,
                ChannelType.EMAIL,
            ]
        }
```
---