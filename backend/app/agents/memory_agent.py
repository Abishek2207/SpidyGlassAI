import time
from app.agents.base_agent import BaseAgent, AgentContext
from app.modules.logs.service import LogsService
from app.core.database import AsyncSessionLocal

class MemoryAgent(BaseAgent):
    """Responsible for persisting context and conversational history."""
    
    def __init__(self):
        super().__init__("Memory Agent")

    async def process(self, context: AgentContext) -> AgentContext:
        start = time.time()
        try:
            # We open a short-lived session here just for persistence
            async with AsyncSessionLocal() as db:
                await LogsService.log_conversation(
                    db=db,
                    user_id=context.user_id,
                    session_id=context.session_id,
                    input_text=context.transcribed_text,
                    translated_input=context.translated_text,
                    ai_response=context.ai_reply,
                    source_language="en-IN",  # TODO: read from context
                    target_language="hi-IN",  # TODO: read from context
                    processing_time_ms=sum(context.processing_times_ms.values())
                )
            self.logger.info("Persisted conversation history.")
        except Exception as e:
            self.logger.error(f"Memory persistence error: {e}")
            context.errors.append(f"MemoryAgent: {str(e)}")
            
        self.log_latency(context, int((time.time() - start) * 1000))
        return context
