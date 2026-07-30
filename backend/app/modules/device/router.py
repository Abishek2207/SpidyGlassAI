import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.modules.device.service import handle_connection, manager
from app.core.security import decode_access_token

router = APIRouter(tags=["Device / WebSocket"])


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, token: str = Query(None)):
    """
    Main real-time WebSocket gateway.
    Requires a valid JWT token as a query parameter.
    """
    if not token:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return
        
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("No user subject in token")
    except Exception:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    client_id = f"user_{user_id}_{uuid.uuid4().hex[:8]}"
    await handle_connection(client_id, ws)


@router.get("/ws/stats", tags=["Device / WebSocket"])
async def ws_stats():
    """Returns number of active WebSocket connections."""
    return {"active_connections": len(manager.active)}
