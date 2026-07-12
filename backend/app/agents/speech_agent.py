import time
from app.agents.base_agent import BaseAgent, AgentContext
from app.modules.speech.service import SpeechService
from app.modules.speech.schema import SpeechTranscribeRequest

class SpeechAgent(BaseAgent):
    """Handles audio processing and transcription via Sarvam AI."""
    
    def __init__(self):
        super().__init__("Speech Agent")
        self.speech_svc = SpeechService()

    async def process(self, context: AgentContext) -> AgentContext:
        if not context.raw_audio:
            self.logger.debug("No audio provided; skipping STT.")
            return context

        start = time.time()
        try:
            req = SpeechTranscribeRequest(
                audio_base64=context.raw_audio,
                language_code="en-IN" # Could be dynamic based on settings
            )
            result = await self.speech_svc.transcribe(req)
            context.transcribed_text = result.transcript
            self.logger.info(f"Transcribed: {result.transcript}")
        except Exception as e:
            self.logger.error(f"STT Error: {e}")
            context.errors.append(f"SpeechAgent: {str(e)}")
            
        self.log_latency(context, int((time.time() - start) * 1000))
        return context
