from litestar import Controller, get


class HealthController(Controller):
    path = ""

    @get("/health")
    async def health_check(self) -> dict:
        return {"status": "healthy", "service": "omnichannel"}
