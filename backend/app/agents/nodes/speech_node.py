from app.agents.state import AgentState
from typing import Dict, Any

async def speech_node(state: AgentState) -> Dict[str, Any]:
    return {"agent_scratchpad": state.get("agent_scratchpad", []) + ["speech executed"]}
