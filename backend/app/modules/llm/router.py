from fastapi import APIRouter, Depends
from app.core.security import get_current_user_id
from app.modules.llm.schema import LLMRequest, LLMResponse
from app.modules.llm.service import LLMService

router = APIRouter(prefix="/llm", tags=["LLM Service"])
_service = LLMService()


@router.post("/chat", response_model=LLMResponse)
async def chat_completion(
    req: LLMRequest,
    _: int = Depends(get_current_user_id),
):
    """Send a chat message to Sarvam AI LLM and get a response."""
    return await _service.chat(req)
