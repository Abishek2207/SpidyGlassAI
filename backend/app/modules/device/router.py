import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.modules.device.service import handle_connection, manager

router = APIRouter(tags=["Device / WebSocket"])


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """
    Main real-time WebSocket gateway.
    No auth required at connection (token can be sent in first message).
    """
    client_id = str(uuid.uuid4())
    await handle_connection(client_id, ws)


@router.get("/ws/stats", tags=["Device / WebSocket"])
async def ws_stats():
    """Returns number of active WebSocket connections."""
    return {"active_connections": len(manager.active)}
