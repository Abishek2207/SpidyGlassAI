import time
from app.agents.base_agent import BaseAgent, AgentContext
from app.modules.tts.service import TTSService
from app.modules.tts.schema import TTSRequest

class TTSAgent(BaseAgent):
    """Handles text-to-speech synthesis via Sarvam AI."""
    
    def __init__(self):
        super().__init__("TTS Agent")
        self.tts_svc = TTSService()

    async def process(self, context: AgentContext) -> AgentContext:
        if not context.ai_reply:
            return context

        start = time.time()
        try:
            req = TTSRequest(
                inputs=[context.ai_reply[:500]], # Sarvam TTS limit
                target_language_code="hi-IN" # Could be dynamic based on settings
            )
            result = await self.tts_svc.synthesize(req)
            if result.audios:
                context.tts_audio = result.audios[0]
            self.logger.info("TTS Synthesis complete.")
        except Exception as e:
            self.logger.error(f"TTS Error: {e}")
            context.errors.append(f"TTSAgent: {str(e)}")
            
        self.log_latency(context, int((time.time() - start) * 1000))
        return context
