from fastapi import APIRouter, HTTPException, Request
from backend.api.models.transaction import TransactionInput
from backend.api.models.analysis_response import AnalysisResponse
from backend.services.react_engine import ReActEngine
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_transaction(
    transaction: TransactionInput,
    request: Request
):
    try:
        # Get engine (instantiate new for isolation or use singleton if stateless)
        # ReActEngine is mostly stateless but holds 'history' which clears per run
        engine = ReActEngine()
        
        # Parse inputs
        tx_dict = transaction.dict()
        cust_history = tx_dict.pop('customer_history', {}) or {}
        
        # Run analysis
        result = engine.run(tx_dict, cust_history)
        
        # Return
        return AnalysisResponse(**result)
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
