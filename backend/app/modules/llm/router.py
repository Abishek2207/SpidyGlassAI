from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user_id
from app.core.database import get_db
from app.modules.llm.schema import LLMRequest, LLMResponse
from app.modules.llm.service import LLMService
from app.modules.logs.service import LogsService

router = APIRouter(prefix="/llm", tags=["LLM Service"])
_service = LLMService()

@router.post("/chat", response_model=LLMResponse)
async def chat_completion(
    req: LLMRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Send a chat message to Sarvam AI LLM and get a response."""
    resp = await _service.chat(req)
    
    input_text = req.messages[-1].content if req.messages else ""
    await LogsService.log_conversation(
        db=db,
        user_id=user_id,
        session_id="chat_" + str(user_id),
        input_text=input_text,
        ai_response=resp.reply,
        processing_time_ms=resp.processing_time_ms
    )
    
    return resp
