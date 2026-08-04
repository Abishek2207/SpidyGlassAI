from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user_id
from app.core.database import get_db
from app.modules.translation.schema import TranslationRequest, TranslationResponse
from app.modules.translation.service import TranslationService
from app.modules.logs.service import LogsService

router = APIRouter(prefix="/translation", tags=["Translation Service"])
_service = TranslationService()

@router.post("/translate", response_model=TranslationResponse)
async def translate_text(
    req: TranslationRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Translate text between Indian languages using Sarvam AI."""
    resp = await _service.translate(req)
    
    await LogsService.log_translation(
        db=db,
        user_id=user_id,
        source_language=req.source_language_code,
        target_language=req.target_language_code,
        char_count=len(req.input),
        processing_time_ms=resp.processing_time_ms
    )
    
    return resp
