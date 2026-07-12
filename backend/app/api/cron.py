from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.modules.logs.service import LogsService

router = APIRouter()

@router.post("/cleanup")
async def cleanup_old_logs(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Cron endpoint to delete logs older than 7 days.
    Triggered securely by Vercel Cron.
    """
    # Verify the cron secret to prevent unauthorized wiping
    expected_token = f"Bearer {settings.CRON_SECRET}" if hasattr(settings, 'CRON_SECRET') and settings.CRON_SECRET else "Bearer spiderglass-local-cron"
    
    if authorization != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid CRON_SECRET"
        )
    
    deleted_count = LogsService.cleanup_old_logs(db, days=7)
    
    return {
        "status": "success",
        "message": f"Successfully deleted {deleted_count} old log entries.",
        "deleted_count": deleted_count
    }
