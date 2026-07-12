"""
SpiderGlass AI – Hardware Interface Providers
Abstract base classes defining the contract for hardware peripherals.
"""
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional

class BaseCameraProvider(ABC):
    """Abstract interface for Camera hardware."""
    
    @abstractmethod
    def start_stream(self) -> None:
        pass
        
    @abstractmethod
    def stop_stream(self) -> None:
        pass
        
    @abstractmethod
    async def read_frame(self) -> Any:
        """Read a single frame from the camera."""
        pass


class BaseAudioProvider(ABC):
    """Abstract interface for Microphone/Audio hardware."""
    
    @abstractmethod
    def start_recording(self) -> None:
        pass
        
    @abstractmethod
    def stop_recording(self) -> None:
        pass
        
    @abstractmethod
    async def read_chunk(self) -> Any:
        """Read an audio chunk from the microphone."""
        pass


class BaseHUDProvider(ABC):
    """Abstract interface for the Heads-Up Display hardware."""
    
    @abstractmethod
    async def render(self, data: Dict[str, Any]) -> None:
        """Render data (text, images, bounding boxes) to the HUD."""
        pass
