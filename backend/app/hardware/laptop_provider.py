"""
SpiderGlass AI – Laptop Hardware Providers
Wraps the WebSocket interface to simulate the smart-glass hardware using a laptop.
"""
import asyncio
from typing import Any, Dict
from app.hardware.base_provider import BaseCameraProvider, BaseAudioProvider, BaseHUDProvider
import logging

logger = logging.getLogger("spiderglass.hardware.laptop")


class LaptopCameraProvider(BaseCameraProvider):
    """Simulates a camera by receiving frames via WebSocket."""
    
    def __init__(self):
        self.frame_queue = asyncio.Queue()
        self.is_streaming = False

    def start_stream(self) -> None:
        self.is_streaming = True
        logger.info("LaptopCameraProvider stream started.")

    def stop_stream(self) -> None:
        self.is_streaming = False
        logger.info("LaptopCameraProvider stream stopped.")

    async def push_frame(self, frame_data: Any) -> None:
        if self.is_streaming:
            await self.frame_queue.put(frame_data)

    async def read_frame(self) -> Any:
        if not self.is_streaming:
            return None
        return await self.frame_queue.get()


class LaptopAudioProvider(BaseAudioProvider):
    """Simulates a microphone by receiving audio chunks via WebSocket."""
    
    def __init__(self):
        self.audio_queue = asyncio.Queue()
        self.is_recording = False

    def start_recording(self) -> None:
        self.is_recording = True
        logger.info("LaptopAudioProvider recording started.")

    def stop_recording(self) -> None:
        self.is_recording = False
        logger.info("LaptopAudioProvider recording stopped.")

    async def push_chunk(self, chunk: Any) -> None:
        if self.is_recording:
            await self.audio_queue.put(chunk)

    async def read_chunk(self) -> Any:
        if not self.is_recording:
            return None
        return await self.audio_queue.get()


class LaptopHUDProvider(BaseHUDProvider):
    """Simulates the HUD by sending data back through the WebSocket connection manager."""
    
    def __init__(self, websocket_manager, client_id: str):
        self.manager = websocket_manager
        self.client_id = client_id

    async def render(self, data: Dict[str, Any]) -> None:
        """Render data to the frontend (HUD)."""
        await self.manager.send(self.client_id, data)
