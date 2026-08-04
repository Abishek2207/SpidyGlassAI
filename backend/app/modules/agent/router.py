from fastapi import APIRouter, Depends
from app.core.security import get_current_user_id
from app.agents.graph import app_graph
from app.agents.state import AgentState
from pydantic import BaseModel

router = APIRouter(prefix="/langgraph", tags=["LangGraph Multi-Agent"])

class LangGraphRequest(BaseModel):
    user_input: str
    session_id: str

@router.post("/invoke")
async def invoke_graph(
    req: LangGraphRequest,
    user_id: int = Depends(get_current_user_id)
):
    initial_state = {
        "session_id": req.session_id,
        "user_id": user_id,
        "user_input": req.user_input,
        "current_intent": "coordinator", # Trigger the coordinator first
        "conversation_history": [],
        "agent_scratchpad": [],
        "retrieved_documents": [],
        "final_response": "",
        "offline_mode": False,
        "errors": []
    }
    
    result = await app_graph.ainvoke(initial_state)
    return {"status": "success", "state": result}
