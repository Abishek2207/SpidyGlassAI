"""
SpiderGlass AI – Agent Router Service
Proxies the REST and WebSocket endpoints into the Multi-Agent Orchestrator.
"""
import uuid
import logging
from app.modules.agent.schema import AgentInput, AgentOutput
from app.agents.base_agent import AgentContext
from app.agents.orchestrator_agent import orchestrator

logger = logging.getLogger("spiderglass.agent_service")


class AgentService:
    """Legacy service wrapper adapting API calls to the new Multi-Agent framework."""

    async def run_pipeline(self, inp: AgentInput, user_id: int = 1) -> AgentOutput:
        # Construct the context
        session_id = inp.session_id or str(uuid.uuid4())
        ctx = AgentContext(
            session_id=session_id,
            user_id=user_id,
            raw_audio=inp.audio_base64
        )
        
        # If text is provided, pretend it was already transcribed
        if inp.text:
            ctx.transcribed_text = inp.text
            
        # Run through the multi-agent orchestrator
        ctx = await orchestrator.process(ctx)

        # Build legacy AgentOutput format for the frontend
        stages = list(ctx.processing_times_ms.keys())
        
        out = AgentOutput(
            transcript=ctx.transcribed_text,
            translated_text=ctx.translated_text,
            ai_reply=ctx.ai_reply,
            tts_audio_base64=ctx.tts_audio,
            pipeline_stages=stages,
            total_processing_time_ms=sum(ctx.processing_times_ms.values())
        )
        
        if ctx.errors:
            out.error = "; ".join(ctx.errors)
            
        return out
