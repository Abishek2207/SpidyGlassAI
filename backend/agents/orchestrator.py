import logging
import asyncio
import time
import random
from typing import Dict, Any
from agents.vision_agent import VisionAgent
from agents.gesture_agent import GestureAgent

logger = logging.getLogger("visionvoice.orchestrator")

class AgentOrchestrator:
    def __init__(self):
        self.clients = {}  
        self.client_counter = 0
        self.vision_agent = None
        self.gesture_agent = None
        self._telemetry_task = None
        logger.info("Agent Orchestrator initialized")

    async def initialize(self):
        logger.info("Initializing sub-agents...")
        self.vision_agent = VisionAgent()
        self.gesture_agent = GestureAgent()
        
        # Start background telemetry broadcast
        self._telemetry_task = asyncio.create_task(self.broadcast_telemetry())

    async def shutdown(self):
        logger.info("Shutting down agents...")
        if self._telemetry_task:
            self._telemetry_task.cancel()

    async def register_client(self, websocket):
        self.client_counter += 1
        client_id = f"client_{self.client_counter}"
        self.clients[client_id] = websocket
        logger.info(f"Registered {client_id}")
        return client_id

    async def unregister_client(self, client_id):
        if client_id in self.clients:
            del self.clients[client_id]
            logger.info(f"Unregistered {client_id}")

    async def broadcast_telemetry(self):
        """Simulates and broadcasts system telemetry like a real HUD"""
        while True:
            try:
                if self.clients:
                    payload = {
                        "type": "telemetry",
                        "data": {
                            "system": {
                                "fps": random.randint(28, 32),
                                "gpu_utilization": random.randint(45, 85),
                                "battery": 78,
                                "latency_ms": random.randint(15, 45)
                            },
                            "agents": {
                                "vision": {"status": "active", "confidence": random.uniform(0.85, 0.99), "latency_ms": random.randint(10, 20)},
                                "speech": {"status": "listening", "confidence": random.uniform(0.70, 0.95), "latency_ms": random.randint(50, 150)},
                                "translation": {"status": "idle", "confidence": 0.0, "latency_ms": 0},
                                "context": {"status": "active", "confidence": random.uniform(0.9, 0.99), "latency_ms": random.randint(5, 10)},
                                "voice": {"status": "idle", "confidence": 0.0, "latency_ms": 0},
                                "safety": {"status": "active", "confidence": 1.0, "latency_ms": random.randint(1, 5)},
                                "device": {"status": "active", "confidence": 1.0, "latency_ms": 0}
                            }
                        }
                    }
                    # Broadcast to all clients
                    disconnected = []
                    for cid, ws in self.clients.items():
                        try:
                            await ws.send_json(payload)
                        except Exception:
                            disconnected.append(cid)
                            
                    for cid in disconnected:
                        await self.unregister_client(cid)

            except Exception as e:
                logger.error(f"Telemetry broadcast error: {e}")
                
            await asyncio.sleep(1.0) # 1Hz update rate for telemetry

    async def dispatch(self, client_id: str, payload: Dict[str, Any]):
        msg_type = payload.get("type")
        data = payload.get("data")
        
        if msg_type == "video_frame":
            start_time = time.time()
            result = self.vision_agent.process_frame(data)
            process_time = int((time.time() - start_time) * 1000)
            
            if result:
                landmarks = result["landmarks"]
                processed_image = result["processed_image"]
                
                gesture = self.gesture_agent.recognize_gesture(landmarks)
                
                response_payload = {
                    "type": "frame_result",
                    "data": {
                        "image": processed_image,
                        "gesture": gesture,
                        "process_time_ms": process_time
                    }
                }
                await self.send_to_client(client_id, response_payload)
        
        elif msg_type == "user_text":
            # Mock text echo
            await self.send_to_client(client_id, {
                "type": "conversation_reply",
                "data": f"AI: I understood '{data}' (Mock Response)"
            })
        else:
            logger.warning(f"Unknown message type: {msg_type}")

    async def send_to_client(self, client_id: str, payload: Dict[str, Any]):
        if client_id in self.clients:
            await self.clients[client_id].send_json(payload)
