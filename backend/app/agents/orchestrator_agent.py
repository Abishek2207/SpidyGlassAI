import uuid
from app.agents.base_agent import BaseAgent, AgentContext
from app.agents.speech_agent import SpeechAgent
from app.agents.translation_agent import TranslationAgent
from app.agents.conversation_agent import ConversationAgent
from app.agents.tts_agent import TTSAgent
from app.agents.memory_agent import MemoryAgent

class OrchestratorAgent(BaseAgent):
    """
    Coordinates the execution of specialized agents in the SpiderGlass pipeline.
    Implements the Chain of Responsibility or a DAG approach.
    """
    
    def __init__(self):
        super().__init__("Orchestrator Agent")
        
        # Initialize the pipeline
        self.agents = [
            SpeechAgent(),
            TranslationAgent(),
            ConversationAgent(),
            TTSAgent(),
            MemoryAgent()
        ]

    async def process(self, context: AgentContext) -> AgentContext:
        self.logger.info(f"Starting orchestration for session {context.session_id}")
        
        for agent in self.agents:
            context = await agent.process(context)
            if context.errors:
                self.logger.error(f"Pipeline halted due to error in {agent.name}: {context.errors[-1]}")
                break
                
        self.logger.info(f"Orchestration complete. Pipeline took {sum(context.processing_times_ms.values())}ms")
        return context

# Singleton instance
orchestrator = OrchestratorAgent()
