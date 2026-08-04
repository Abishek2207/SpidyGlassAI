from app.agents.state import AgentState
from typing import Dict, Any

async def scheduler_node(state: AgentState) -> Dict[str, Any]:
    return {"agent_scratchpad": state.get("agent_scratchpad", []) + ["scheduler executed"]}
