from typing import Dict, Any, Generator
from datetime import datetime
import logging

# Original Coordinator Agent
from backend.agents.coordinator_agent import CoordinatorAgent

logger = logging.getLogger(__name__)

class ReActEngine:
    """Wrapper for the Coordinator Agent"""
    
    def __init__(self):
        self.coordinator = CoordinatorAgent()
        
    def run(self, transaction: Dict[str, Any], customer_history: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Execute analysis via LangChain Agent.
        """
        start_time = datetime.now()
        
        # Call the LangChain agent
        # The agent returns a dictionary with 'decision', 'react_steps', etc.
        result = self.coordinator.analyze(transaction, customer_history)
        
        # Ensure we return expected format
        if 'processing_time_ms' not in result or result['processing_time_ms'] == 0:
            result['processing_time_ms'] = int((datetime.now() - start_time).total_seconds() * 1000)
            
        return result

    async def arun(self, transaction: Dict[str, Any], customer_history: Dict[str, Any] = {}, callbacks: list = None) -> Dict[str, Any]:
        """
        Async execute analysis via Coordinator Agent.
        """
        start_time = datetime.now()
        
        # Call the coordinator agent async
        result = await self.coordinator.analyze_async(transaction, customer_history, callbacks=callbacks)
        
        # Ensure we return expected format
        if 'processing_time_ms' not in result or result['processing_time_ms'] == 0:
            result['processing_time_ms'] = int((datetime.now() - start_time).total_seconds() * 1000)
            
        return result

    def stream_analysis(self, transaction: Dict[str, Any], customer_history: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """
        Stream analysis steps. 
        DEPRECATED: Use arun with WebSocketCallbackHandler for true real-time streaming.
        This remains for backward compatibility or testing.
        """
        # Execute SyncWrapper?
        # For simplicity, we just run sync run() here
        full_result = self.run(transaction, customer_history)
        
        # Determine risk score if missing (fallback)
        risk_score = full_result.get('risk_score', 0)
        
        # Yield Steps
        for step in full_result.get('react_steps', []):
            yield {"type": "react_step", "data": step}
            
        # Yield Final Decision
        yield {"type": "decision", "data": full_result}
