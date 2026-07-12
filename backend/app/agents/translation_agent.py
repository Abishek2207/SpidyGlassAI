import time
from app.agents.base_agent import BaseAgent, AgentContext
from app.modules.translation.service import TranslationService
from app.modules.translation.schema import TranslationRequest

class TranslationAgent(BaseAgent):
    """Handles text translation via Sarvam AI."""
    
    def __init__(self):
        super().__init__("Translation Agent")
        self.translation_svc = TranslationService()

    async def process(self, context: AgentContext) -> AgentContext:
        text_to_translate = context.transcribed_text
        if not text_to_translate:
            return context

        # For simplicity in this iteration, we mock the language pairs.
        # In full production, this would read from user settings via ContextAgent.
        source_lang = "en-IN"
        target_lang = "hi-IN"

        if source_lang == target_lang:
            context.translated_text = text_to_translate
            return context

        start = time.time()
        try:
            req = TranslationRequest(
                input=text_to_translate,
                source_language_code=source_lang,
                target_language_code=target_lang
            )
            result = await self.translation_svc.translate(req)
            context.translated_text = result.translated_text
            self.logger.info(f"Translated: {result.translated_text}")
        except Exception as e:
            self.logger.error(f"Translation Error: {e}")
            context.errors.append(f"TranslationAgent: {str(e)}")
            
        self.log_latency(context, int((time.time() - start) * 1000))
        return context
