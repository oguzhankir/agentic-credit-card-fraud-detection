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
        # Get engine
        engine = ReActEngine()
        
        # Parse inputs
        tx_dict = transaction.dict()
        cust_history = tx_dict.pop('customer_history', {}) or {}
        connection_id = tx_dict.pop('connection_id', None)
        
        callbacks = []
        if connection_id:
            from backend.services.callbacks import WebSocketCallbackHandler
            
            # Access WS manager from app state
            ws_manager = request.app.state.ws_manager
            
            # Create callback
            ws_callback = WebSocketCallbackHandler(ws_manager, connection_id)
            callbacks.append(ws_callback)
        
        # Run analysis ASYNC
        result = await engine.arun(tx_dict, cust_history, callbacks=callbacks)
        
        # Return
        return AnalysisResponse(**result)
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
