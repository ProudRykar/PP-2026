## def test_message_creation:

```python
def test_message_creation():
    msg = Message(
        id="test:123",
        channel=ChannelType.TELEGRAM,
        sender="user123",
        content="Hello, world!",
        timestamp=datetime.now(),
        metadata={"test": True},
    )

    assert msg.id == "test:123"
    assert msg.channel == ChannelType.TELEGRAM
    assert msg.sender == "user123"
    assert msg.content == "Hello, world!"
    assert msg.to_dict()["channel"] == ChannelType.TELEGRAM
```
---
## def test_channel_types:

```python
def test_channel_types():
    assert ChannelType.TELEGRAM == "telegram"
    assert ChannelType.EMAIL == "email"
    assert ChannelType.SLACK == "slack"
    assert ChannelType.DISCORD == "discord"
    assert ChannelType.VK == "vk"
```
---
## def test_message_service:

```python
@pytest.mark.asyncio
async def test_message_service():
    from app.core.services.message_service import MessageService
    from app.adapters.repositories.postgres.repository import PostgresMessageRepository
    from app.adapters.gateways.postgres import PostgresDatabaseGateway

    db = PostgresDatabaseGateway()
    repo = PostgresMessageRepository(db)
    service = MessageService(repo)

    assert service is not None
```
---