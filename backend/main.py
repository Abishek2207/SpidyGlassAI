from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import logging
from agents.orchestrator import AgentOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("visionvoice")

app = FastAPI(title="VisionVoice AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = AgentOrchestrator()

@app.on_event("startup")
async def startup_event():
    logger.info("VisionVoice AI backend started. Initializing agents...")
    await orchestrator.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("VisionVoice AI backend shutting down...")
    await orchestrator.shutdown()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "VisionVoice AI API is running"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("New WebSocket connection accepted")
    
    # Register this connection with the orchestrator
    client_id = await orchestrator.register_client(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                # Dispatch payload to orchestrator
                await orchestrator.dispatch(client_id, payload)
            except json.JSONDecodeError:
                logger.error("Failed to decode JSON from websocket")
    except WebSocketDisconnect:
        logger.info(f"WebSocket client {client_id} disconnected")
        await orchestrator.unregister_client(client_id)
