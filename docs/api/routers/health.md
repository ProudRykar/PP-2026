## Класс HealthController


```python
class HealthController(Controller):
    path = ""
```

---
## def health_check:
#### Маршрут:
- **Декоратор:** @get
- **Маршрут:** `/health`


```python
    @get("/health")
    async def health_check(self) -> dict:
        return {"status": "healthy", "service": "omnichannel"}
```
---