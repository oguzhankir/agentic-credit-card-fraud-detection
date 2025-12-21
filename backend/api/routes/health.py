from fastapi import APIRouter, Request
from datetime import datetime

router = APIRouter(prefix="/api/health", tags=["health"])

@router.get("")
async def health_check(request: Request):
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Fraud Detection Agentic AI",
        "checks": {
            "model_service_ready": True, 
            "llm_service_ready": True
        }
    }
