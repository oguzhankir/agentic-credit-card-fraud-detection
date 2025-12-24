from typing import Dict, Generator, Any
from pathlib import Path
import json
import uuid
import logging
from datetime import datetime, date
from backend.agents.coordinator_agent import CoordinatorAgent
from backend.config.settings import settings

logger = logging.getLogger(__name__)

class ReActOrchestrator:
    """
    Orchestrates ReAct loop execution and logging.
    """
    
    def __init__(self):
        """Initialize coordinator agent and logging."""
        self.coordinator = CoordinatorAgent()
        self.log_dir = Path(settings.react_log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def run(self, transaction: dict) -> dict:
        """
        Execute full analysis with ReAct logging.
        
        Args:
            transaction: Raw transaction data
            
        Returns:
            Complete analysis with decision and all steps
        """
        transaction_id = str(uuid.uuid4())
        logger.info(f"Starting analysis for transaction {transaction_id}")
        
        start_time = datetime.now()
        
        try:
            # Execute Coordinator Analysis
            result = self.coordinator.analyze(transaction)
            
            # Extract Components
            decision = result.get("decision", {})
            react_steps = result.get("react_steps", [])
            
            # Calculate metrics
            processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Estimate risk score from steps if calculator was called
            # OR parse from decision if coordinator put it there.
            # Simpler: Extract from tool call in history if available, or 0.
            # But usually the coordinator output includes reasoning.
            # Let's extract from the tool output in the steps if risk_scorer was used.
            risk_score = 0
            for step in reversed(react_steps):
                if step["type"] == "OBSERVATION":
                    try:
                        # Sometimes observation is JSON string
                        obs_data = step["content"]
                        if isinstance(obs_data, str) and "risk_score" in obs_data:
                             # Handle stringified json
                             # simple heuristic for now as robust parsing is complex
                             pass
                    except:
                        pass
            
            # Construct Final Response Object to be saved
            final_output = {
                "transaction_id": transaction_id,
                "timestamp": datetime.now().isoformat(),
                "input_transaction": transaction,
                "decision": decision,
                "react_steps": react_steps,
                "metrics": {
                    "processing_time_ms": int(processing_time_ms),
                    "total_tokens_used": result.get("token_usage", {}).get("total_tokens", 0)
                }
            }
            
            # Save Log
            if settings.save_react_logs:
                self._save_react_log(transaction_id, final_output)
            
            return final_output
            
        except Exception as e:
            logger.error(f"Orchestration failed: {e}", exc_info=True)
            raise e

    async def stream(self, transaction: dict) -> Generator[Dict, None, None]:
        """
        Generator that yields steps in real-time for WebSocket.
        Uses asyncio.Queue and callback handler to stream events from
        the blocking agent execution running in a separate thread.
        """
        import asyncio
        from backend.services.streaming_callback import StreamingReActCallbackHandler
        from concurrent.futures import ThreadPoolExecutor
        
        # Create queue for events
        queue = asyncio.Queue()
        callback = StreamingReActCallbackHandler(queue)
        
        start_time = datetime.now()
        result = None
        
        # Function to run analysis in thread
        def run_analysis():
            try:
                result = self.coordinator.analyze(transaction, callbacks=[callback])
                # Put complete signal
                return result
            except Exception as e:
                logger.error(f"Analysis thread failed: {e}")
                raise e

        # Run blocking analysis in separate thread to avoid blocking event loop
        loop = asyncio.get_event_loop()
        # Create task for analysis
        analysis_task = loop.run_in_executor(None, run_analysis)
        
        while True:
            # Wait for next token or task completion
            # usage of asyncio.wait to wait for either queue item or task finish
            
            # create queue get task
            queue_task = asyncio.create_task(queue.get())
            
            done, pending = await asyncio.wait(
                [queue_task, analysis_task], 
                return_when=asyncio.FIRST_COMPLETED
            )
            
            if queue_task in done:
                # Value available in queue
                event = getattr(queue_task, 'result')() # or queue_task.result()
                yield event
                
                # Check if analysis is also done (race condition or end)
                if analysis_task.done():
                   # Flush queue? The queue might still have items if we consumed faster than put?
                   # Actually if analysis is done, we should empty the queue.
                   # But let's just continue loop until queue is empty AND analysis is done.
                   pass
            
            if analysis_task in done:
                # Analysis finished. 
                # Cancel pending queue wait if any (though we check queue first above)
                if not queue_task.done():
                     # Check if queue has items remaining?
                     # queue.get() waits. If task is done, maybe no more items?
                     # We should drain queue.
                     queue_task.cancel()
                
                # Check for exceptions
                try:
                    result = analysis_task.result()
                    # analysis finished successfully
                    # Drain remaining queue items
                    while not queue.empty():
                        yield queue.get_nowait()
                        
                    # Yield completion event
                    yield {"type": "complete", "analysis": result}
                    break
                    
                except Exception as e:
                    yield {"type": "error", "content": str(e)}
                    break
        
        # Calculate metrics after loop finishes
        processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        if result:
            # Construct Final Response Object (mirrors run() logic)
            final_output = {
                "transaction_id": str(uuid.uuid4()), # New ID or reuse if transaction had one
                "timestamp": datetime.now().isoformat(),
                "input_transaction": transaction,
                "decision": result.get("decision", {}),
                "react_steps": result.get("react_steps", []),
                "metrics": {
                    "processing_time_ms": int(processing_time_ms),
                    "total_tokens_used": result.get("token_usage", {}).get("total_tokens", 0)
                }
            }
            
            # Save Log for WebSocket flows
            if settings.save_react_logs:
                self._save_react_log(final_output["transaction_id"], final_output)
                
            yield {"type": "complete", "analysis": final_output}

    def _save_react_log(self, transaction_id: str, data: Dict):
        """
        Save ReAct steps to JSON file for demo backup.
        
        Saves to: logs/react_logs/YYYY-MM-DD/transaction_{id}.json
        """
        try:
            today_str = date.today().isoformat()
            daily_dir = self.log_dir / today_str
            daily_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = daily_dir / f"transaction_{transaction_id}.json"
            
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
                
            logger.info(f"Saved ReAct log to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save ReAct log: {e}")
