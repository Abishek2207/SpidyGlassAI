import time
from app.agents.base_agent import BaseAgent, AgentContext
from app.modules.llm.service import LLMService
from app.modules.llm.schema import LLMRequest, LLMMessage

class ConversationAgent(BaseAgent):
    """Handles LLM conversational logic."""
    
    def __init__(self):
        super().__init__("Conversation Agent")
        self.llm_svc = LLMService()

    async def process(self, context: AgentContext) -> AgentContext:
        input_text = context.translated_text or context.transcribed_text
        if not input_text:
            return context

        start = time.time()
        try:
            req = LLMRequest(
                messages=[LLMMessage(role="user", content=input_text)]
            )
            result = await self.llm_svc.chat(req)
            context.ai_reply = result.reply
            self.logger.info(f"AI Reply: {result.reply}")
        except Exception as e:
            self.logger.error(f"LLM Error: {e}")
            context.errors.append(f"ConversationAgent: {str(e)}")
            
        self.log_latency(context, int((time.time() - start) * 1000))
        return context
