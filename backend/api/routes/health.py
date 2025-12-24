from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "ok", "service": "fraud-detection-backend"}
