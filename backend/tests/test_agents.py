import pytest
from app.agents.base_agent import AgentContext
from app.agents.orchestrator_agent import OrchestratorAgent

@pytest.mark.asyncio
async def test_orchestrator_initialization():
    """Test that the orchestrator initializes all agents properly."""
    orchestrator = OrchestratorAgent()
    assert len(orchestrator.agents) == 5
    names = [agent.name for agent in orchestrator.agents]
    assert "Speech Agent" in names
    assert "Translation Agent" in names
    assert "Conversation Agent" in names
    assert "TTS Agent" in names
    assert "Memory Agent" in names

@pytest.mark.asyncio
async def test_orchestrator_empty_context():
    """Test that an empty context passes through without error."""
    orchestrator = OrchestratorAgent()
    ctx = AgentContext(session_id="test_session", user_id=1)
    
    result = await orchestrator.process(ctx)
    
    # Should complete with no errors and the Memory Agent should have executed
    assert len(result.errors) == 0
    assert result.session_id == "test_session"
    assert "Memory Agent" in result.processing_times_ms
