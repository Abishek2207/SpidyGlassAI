"""
SpiderGlass AI – Multi-Agent Framework Base.
Defines the standard interface for all AI Agents in the system.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger("spiderglass.agents")


class AgentContext(BaseModel):
    """Context passed between agents during a pipeline run."""
    session_id: str
    user_id: int
    raw_audio: Optional[str] = None
    raw_video_frames: list[str] = []
    
    # State accumulated across agents
    detected_gestures: list[Dict[str, Any]] = []
    transcribed_text: Optional[str] = None
    translated_text: Optional[str] = None
    conversation_history: list[Dict[str, str]] = []
    ai_reply: Optional[str] = None
    tts_audio: Optional[str] = None
    
    # Metadata
    processing_times_ms: Dict[str, int] = {}
    errors: list[str] = []


class BaseAgent(ABC):
    """Abstract Base Class for all SpiderGlass AI Agents."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logger.getChild(self.name.lower().replace(" ", "_"))

    @abstractmethod
    async def process(self, context: AgentContext) -> AgentContext:
        """
        Process the given context, mutate it with results, and return it.
        Each agent implements its specific domain logic here.
        """
        pass

    def log_latency(self, context: AgentContext, ms: int):
        """Helper to record this agent's latency in the context."""
        context.processing_times_ms[self.name] = ms
        self.logger.debug(f"Completed in {ms}ms")
