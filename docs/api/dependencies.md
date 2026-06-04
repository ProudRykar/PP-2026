## def get_message_service:

```python
def get_message_service() -> MessageService:
    container = get_container()
    return container.resolve(MessageService)
```
---