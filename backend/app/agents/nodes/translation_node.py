from app.agents.state import AgentState
from typing import Dict, Any

async def translation_node(state: AgentState) -> Dict[str, Any]:
    return {"agent_scratchpad": state.get("agent_scratchpad", []) + ["translation executed"]}
