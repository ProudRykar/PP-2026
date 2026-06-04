import logging
from typing import Any

from litestar import WebSocket

logger = logging.getLogger(__name__)

websocket_connections: list[WebSocket] = []


async def broadcast_message(message: dict[str, Any]) -> None:
    stale = []
    for connection in websocket_connections:
        try:
            await connection.send_json(message)
        except Exception:
            stale.append(connection)
    for conn in stale:
        try:
            websocket_connections.remove(conn)
        except ValueError:
            pass
