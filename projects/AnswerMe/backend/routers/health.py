from fastapi import APIRouter, HTTPException
import logging
from datetime import datetime

from config import settings
from models.schemas import HealthResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("/", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    try:
        return HealthResponse(
            status="healthy",
            version=settings.APP_VERSION,
            timestamp=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
