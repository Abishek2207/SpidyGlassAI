from app.agents.state import AgentState
from typing import Dict, Any

async def conversation_node(state: AgentState) -> Dict[str, Any]:
    return {"agent_scratchpad": state.get("agent_scratchpad", []) + ["conversation executed"]}
