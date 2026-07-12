from fastapi import APIRouter, Depends
from app.core.security import get_current_user_id
from app.modules.translation.schema import TranslationRequest, TranslationResponse
from app.modules.translation.service import TranslationService

router = APIRouter(prefix="/translation", tags=["Translation Service"])
_service = TranslationService()


@router.post("/translate", response_model=TranslationResponse)
async def translate_text(
    req: TranslationRequest,
    _: int = Depends(get_current_user_id),
):
    """Translate text between Indian languages using Sarvam AI."""
    return await _service.translate(req)
