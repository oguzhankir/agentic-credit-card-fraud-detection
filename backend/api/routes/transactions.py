from fastapi import APIRouter, HTTPException, BackgroundTasks
from backend.api.schemas.transaction import TransactionInput
from backend.api.schemas.response import AnalysisResponse
from backend.services.react_orchestrator import ReActOrchestrator
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

orchestrator = ReActOrchestrator()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_transaction(
    transaction: TransactionInput,
    background_tasks: BackgroundTasks
):
    """
    Trigger Agentic Fraud Analysis for a transaction.
    """
    try:
        # Convert Pydantic model to dict
        transaction_dict = transaction.model_dump()
        
        # Run Synchronous Analysis (for this v1 implementation)
        # In a high-scale real app, we'd push to a queue and return ID, 
        # but for this demo/MVP we wait for result (~5-10s).
        result = orchestrator.run(transaction_dict)
        
        return result
        
    except Exception as e:
        logger.error(f"Analysis request failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
