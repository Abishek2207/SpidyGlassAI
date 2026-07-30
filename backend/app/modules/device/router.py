import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.modules.device.service import handle_connection, manager

router = APIRouter(tags=["Device / WebSocket"])


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, token: str = Query(None), demoMode: str = Query("true")):
    """
    Main real-time WebSocket gateway.
    Token is optional - auth bypassed for open access mode.
    """
    # Use token as user ID if provided, otherwise generate anonymous session
    if token:
        try:
            from app.core.security import decode_access_token
            payload = decode_access_token(token)
            user_id = payload.get("sub", "anon")
        except Exception:
            user_id = "anon"
    else:
        user_id = "anon"

    is_demo = demoMode.lower() == "true"
    client_id = f"user_{user_id}_{uuid.uuid4().hex[:8]}"
    await handle_connection(client_id, ws, is_demo)



@router.get("/ws/stats", tags=["Device / WebSocket"])
async def ws_stats():
    """Returns number of active WebSocket connections."""
    return {"active_connections": len(manager.active)}
