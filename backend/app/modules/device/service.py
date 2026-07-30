"""
SpiderGlass AI – WebSocket Device Service
Manages all real-time connections.

Protocol (JSON messages):
  Client → Server:
    { "type": "video_frame",  "data": "<base64>" }
    { "type": "audio_chunk",  "data": "<base64>" }
    { "type": "text_message", "data": "<string>" }
    { "type": "audio_end" }
    { "type": "ping" }

  Server → Client:
    { "type": "telemetry",      "data": { system: ..., agents: ... } }
    { "type": "frame_result",   "data": { image, gesture, hands, process_time_ms } }
    { "type": "agent_response", "data": { transcript, translated_text, ai_reply, ... } }
    { "type": "system_log",     "data": { timestamp, message, level, module } }
    { "type": "pong" }
    { "type": "error",          "data": "<message>" }
"""
import asyncio
import json
import time
import logging
import random
import psutil
from fastapi import WebSocket, WebSocketDisconnect
from app.modules.camera.service import CameraService
from app.modules.camera.schema import CameraFrameRequest
from app.modules.gesture.service import GestureService
from app.modules.gesture.schema import GestureRecognizeRequest, Landmark
from app.modules.agent.service import AgentService
from app.modules.agent.schema import AgentInput

logger = logging.getLogger("spiderglass.device")

_camera_svc = CameraService()
_gesture_svc = GestureService()
_agent_svc = AgentService()

# Track per-agent latency for live Agent Mesh display
_agent_latency: dict = {
    "vision":       {"latency_ms": 0, "task": "Awaiting Frames",         "last_update": time.time()},
    "speech":       {"latency_ms": 0, "task": "Awaiting Audio",           "last_update": time.time()},
    "translation":  {"latency_ms": 0, "task": "Idle",                    "last_update": time.time()},
    "conversation": {"latency_ms": 0, "task": "Idle",                    "last_update": time.time()},
    "context":      {"latency_ms": 2, "task": "Background Processing",   "last_update": time.time()},
    "memory":       {"latency_ms": 1, "task": "Syncing Session Data",     "last_update": time.time()},
    "device":       {"latency_ms": 0, "task": "WebSocket Streaming",      "last_update": time.time()},
}


DEMO_LOG_MESSAGES = [
    ("vision",       "Hand landmarks extracted — 21 keypoints per hand detected.",              "info"),
    ("speech",       "Audio buffer flushed — STT pipeline triggered.",                          "info"),
    ("translation",  "Translation pipeline idle — awaiting transcribed text.",                  "info"),
    ("conversation", "LLM context window loaded — 4096 token capacity.",                        "info"),
    ("memory",       "Session memory synced — 3 prior context turns retained.",                 "info"),
    ("device",       "WebSocket heartbeat acknowledged — connection latency nominal.",           "debug"),
    ("vision",       "MediaPipe Hands model loaded — inference running at ~18ms per frame.",    "info"),
    ("context",      "Context agent processing background telemetry — CPU/RAM within limits.", "debug"),
    ("speech",       "Microphone stream active — audio chunks accumulating in buffer.",         "info"),
    ("vision",       "Gesture classifier output: Open Palm (Hello) — confidence 0.95.",        "info"),
    ("conversation", "Demo LLM response dispatched — Sarvam API key not configured.",          "warn"),
    ("translation",  "Demo translation returned — Sarvam API key not configured.",             "warn"),
    ("device",       "Telemetry broadcast complete — 7 agent states updated.",                  "debug"),
    ("memory",       "Conversation turn appended to session memory.",                           "info"),
    ("vision",       "Face bounding box detected — confidence 0.87.",                          "info"),
]


class ConnectionManager:
    """Manages all active WebSocket connections."""

    def __init__(self):
        self.active: dict[str, WebSocket] = {}

    async def connect(self, client_id: str, ws: WebSocket):
        await ws.accept()
        self.active[client_id] = ws
        logger.info(f"Client connected: {client_id}  (total={len(self.active)})")

    def disconnect(self, client_id: str):
        self.active.pop(client_id, None)
        logger.info(f"Client disconnected: {client_id}  (total={len(self.active)})")

    async def send(self, client_id: str, payload: dict):
        ws = self.active.get(client_id)
        if ws:
            try:
                await ws.send_text(json.dumps(payload))
            except Exception as e:
                logger.warning(f"Send failed for {client_id}: {e}")
                self.disconnect(client_id)

    async def broadcast(self, payload: dict):
        dead = []
        for cid, ws in list(self.active.items()):
            try:
                await ws.send_text(json.dumps(payload))
            except Exception:
                dead.append(cid)
        for cid in dead:
            self.disconnect(cid)


manager = ConnectionManager()


def _build_telemetry_payload() -> dict:
    """Generate a realistic system + agent telemetry payload using real OS metrics."""
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    now = time.time()

    agents = {}
    for name, meta in _agent_latency.items():
        agents[name] = {
            "status":      "online",
            "task":        meta["task"],
            "confidence":  round(random.uniform(0.92, 0.99), 3),
            "latency_ms":  meta["latency_ms"],
            "last_update": meta["last_update"],
        }

    return {
        "type": "telemetry",
        "data": {
            "system": {
                "fps":              18,
                "gpu_utilization":  0,
                "cpu_utilization":  cpu,
                "ram_utilization":  ram,
                "battery":          100,
                "latency_ms":       15,
                "uptime_seconds":   int(now - psutil.boot_time()),
            },
            "agents": agents,
        },
        "ts": now,
    }


async def _telemetry_loop(client_id: str):
    """Pushes 1 Hz telemetry + live system logs to a specific client."""
    log_index = 0

    while client_id in manager.active:
        # 1. Send system telemetry every second
        await manager.send(client_id, _build_telemetry_payload())

        # 2. Send a system log entry every 3 seconds (rotate through all messages)
        if int(time.time()) % 3 == 0:
            module, message, level = DEMO_LOG_MESSAGES[log_index % len(DEMO_LOG_MESSAGES)]
            log_index += 1
            await manager.send(client_id, {
                "type": "system_log",
                "data": {
                    "timestamp": time.time(),
                    "module":    module,
                    "message":   f"[{module.upper()}] {message}",
                    "level":     level,
                }
            })

        await asyncio.sleep(1.0)


async def _process_frame(client_id: str, data: str):
    """Process a single video frame through the CV pipeline."""
    t_start = time.time()

    try:
        cam_result = await _camera_svc.process_frame(CameraFrameRequest(image_base64=data))

        gesture_results = []
        current_sentence = ""

        if cam_result.hands_detected:
            try:
                import base64
                from io import BytesIO
                from PIL import Image
                import mediapipe as mp
                import numpy as np

                header, encoded = data.split(",", 1) if "," in data else ("", data)
                img_bytes = base64.b64decode(encoded)
                pil_img = Image.open(BytesIO(img_bytes))

                mp_hands = mp.solutions.hands
                with mp_hands.Hands(static_image_mode=True, max_num_hands=2,
                                    min_detection_confidence=0.6) as hands:
                    img_rgb = np.array(pil_img.convert("RGB"))
                    res = hands.process(img_rgb)

                    if res.multi_hand_landmarks:
                        for hlm in res.multi_hand_landmarks:
                            hand_lms = [Landmark(x=lm.x, y=lm.y, z=lm.z) for lm in hlm.landmark]
                            g_req = GestureRecognizeRequest(landmarks=[hand_lms])
                            g_resp, current_sentence = await _gesture_svc.recognize(
                                g_req, session_id=client_id
                            )
                            gesture_results.extend([r.model_dump() for r in g_resp.results])
            except ImportError:
                pass  # vision libs not available — camera mock mode already returned passthrough
            except Exception as ge:
                logger.warning(f"Gesture extraction failed: {ge}")

        latency_ms = int((time.time() - t_start) * 1000)
        _agent_latency["vision"]["latency_ms"] = latency_ms
        _agent_latency["vision"]["task"] = (
            f"Hands: {cam_result.hands_detected} | Faces: {len(cam_result.faces)}"
            if cam_result.hands_detected or cam_result.faces
            else "Scanning Frame"
        )
        _agent_latency["vision"]["last_update"] = time.time()

        from app.hardware.laptop_provider import LaptopHUDProvider
        hud_provider = LaptopHUDProvider(manager, client_id)
        await hud_provider.render({
            "type": "frame_result",
            "data": {
                "image":          cam_result.annotated_image_base64,
                "hands_detected": cam_result.hands_detected,
                "objects":        [o.model_dump() for o in cam_result.objects],
                "faces":          [f.model_dump() for f in cam_result.faces],
                "gestures":       gesture_results,
                "sentence":       current_sentence,
                "process_time_ms": latency_ms,
            },
        })

        # If gesture service produced a confirmed sentence, route it through
        # the full agent pipeline (translation + LLM) automatically.
        if current_sentence:
            asyncio.create_task(_process_text(client_id, current_sentence))

    except Exception as e:
        logger.error(f"Frame processing error: {e}")
        await manager.send(client_id, {"type": "error", "data": str(e)})


async def _process_text(client_id: str, data: str):
    """Run text through the full agent pipeline."""
    t_start = time.time()

    # Update agent states to "processing"
    for name in ("speech", "translation", "conversation"):
        _agent_latency[name]["task"] = "Processing..."
        _agent_latency[name]["last_update"] = time.time()

    try:
        agent_out = await _agent_svc.run_pipeline(AgentInput(text=data))
        total_ms = int((time.time() - t_start) * 1000)

        # Update individual latencies from pipeline_stages timing
        stages = agent_out.pipeline_stages or []
        _agent_latency["speech"]["task"]        = "Transcription complete"
        _agent_latency["translation"]["task"]   = "Translation complete"
        _agent_latency["conversation"]["task"]  = "Response generated"
        for name in ("speech", "translation", "conversation"):
            _agent_latency[name]["latency_ms"]   = total_ms // 3
            _agent_latency[name]["last_update"]  = time.time()

        await manager.send(client_id, {
            "type": "agent_response",
            "data": agent_out.model_dump(),
        })

    except Exception as e:
        logger.error(f"Agent pipeline error: {e}")
        for name in ("speech", "translation", "conversation"):
            _agent_latency[name]["task"] = "Error — see logs"
        await manager.send(client_id, {"type": "error", "data": str(e)})


async def _process_audio(client_id: str, chunks: list[str]):
    """Decode and run accumulated audio through the full pipeline."""
    t_start = time.time()

    _agent_latency["speech"]["task"] = "Transcribing audio..."
    _agent_latency["speech"]["last_update"] = time.time()

    try:
        import base64
        combined_bytes = b"".join([base64.b64decode(c) for c in chunks])
        combined_base64 = base64.b64encode(combined_bytes).decode("utf-8")

        agent_out = await _agent_svc.run_pipeline(AgentInput(audio_base64=combined_base64))
        latency_ms = int((time.time() - t_start) * 1000)

        _agent_latency["speech"]["latency_ms"]   = latency_ms
        _agent_latency["speech"]["task"]         = "Transcription complete"
        _agent_latency["speech"]["last_update"]  = time.time()

        await manager.send(client_id, {
            "type": "agent_response",
            "data": agent_out.model_dump(),
        })
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        _agent_latency["speech"]["task"] = "Error — see logs"
        await manager.send(client_id, {"type": "error", "data": str(e)})


async def handle_connection(client_id: str, ws: WebSocket, demo_mode: bool = True):
    """Main coroutine managing the lifecycle of a single WebSocket client."""
    await manager.connect(client_id, ws)

    # Audio buffer per session
    audio_buffer: list[str] = []

    # Start background telemetry push for this client
    telemetry_task = asyncio.create_task(_telemetry_loop(client_id))

    # Send a welcome log immediately
    await manager.send(client_id, {
        "type": "system_log",
        "data": {
            "timestamp": time.time(),
            "module":    "device",
            "message":   "[DEVICE] WebSocket session established — SpiderGlass AI online.",
            "level":     "info",
        }
    })

    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await manager.send(client_id, {"type": "error", "data": "Invalid JSON"})
                continue

            msg_type = msg.get("type")
            data = msg.get("data")

            # ── Ping ──────────────────────────────────────────────────────────
            if msg_type == "ping":
                _agent_latency["device"]["task"] = "Heartbeat"
                _agent_latency["device"]["last_update"] = time.time()
                await manager.send(client_id, {"type": "pong"})

            # ── Video Frame ───────────────────────────────────────────────────
            elif msg_type == "frame" and data:
                asyncio.create_task(_process_frame(client_id, data))

            # ── Text Message → Full Agent Pipeline ────────────────────────────
            elif msg_type == "text_message" and data:
                asyncio.create_task(_process_text(client_id, data))

            # ── Audio Chunk → Buffer ──────────────────────────────────────────
            elif msg_type == "audio_chunk" and data:
                audio_buffer.append(data)
                _agent_latency["speech"]["task"] = f"Buffering audio ({len(audio_buffer)} chunks)"
                _agent_latency["speech"]["last_update"] = time.time()

            # ── Audio End → Flush ─────────────────────────────────────────────
            elif msg_type == "audio_end":
                if audio_buffer:
                    chunks = audio_buffer.copy()
                    audio_buffer.clear()
                    asyncio.create_task(_process_audio(client_id, chunks))
                else:
                    logger.debug(f"audio_end received but buffer empty for {client_id}")

            else:
                logger.debug(f"Unknown message type '{msg_type}' from {client_id}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected cleanly: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
    finally:
        telemetry_task.cancel()
        manager.disconnect(client_id)
