from fastapi import APIRouter, Depends
from app.core.security import get_current_user_id
from app.modules.agent.schema import AgentInput, AgentOutput
from app.modules.agent.service import AgentService

router = APIRouter(prefix="/agent", tags=["Agent Orchestrator"])
_service = AgentService()


@router.post("/run", response_model=AgentOutput)
async def run_agent_pipeline(
    inp: AgentInput,
    _: int = Depends(get_current_user_id),
):
    """
    Run the full AI pipeline: STT → Translation → LLM → TTS.
    Accepts text, audio, or image as input.
    """
    return await _service.run_pipeline(inp)
