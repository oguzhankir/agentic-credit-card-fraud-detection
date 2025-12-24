from typing import Any, Dict, List, Optional
from uuid import UUID
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.agents import AgentAction, AgentFinish
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class StreamingReActCallbackHandler(BaseCallbackHandler):
    """
    Callback handler that acts as a bridge between LangChain's sync callbacks
    and an asyncio Queue for WebSocket streaming.
    """
    
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue
        self.step_count = 0

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        # Optional: Notify that thinking started
        pass

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Run when chain starts running."""
        pass

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Run on agent action (THOUGHT + ACTION)."""
        self.step_count += 1
        
        # Parse thought from log
        thought = action.log.split("\n")[0] if action.log else f"Planning {action.tool}"
        
        # 1. Emit THOUGHT
        self.queue.put_nowait({
            "type": "thought",
            "step": (self.step_count * 2) - 1,
            "agent": "coordinator", # We assume coordinator for now, or infer from tool
            "content": thought,
            "timestamp": datetime.now().isoformat(),
            "metadata": {"tool": action.tool}
        })
        
        # 2. Emit ACTION
        self.queue.put_nowait({
            "type": "action",
            "step": (self.step_count * 2),
            "agent": "coordinator",
            "content": f"Calling tool: {action.tool}",
            "timestamp": datetime.now().isoformat(),
            "metadata": {"tool": action.tool, "tool_input": str(action.tool_input)}
        })

    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        """Run when tool ends (OBSERVATION)."""
        # 3. Emit OBSERVATION
        # We don't increment step count here to align with ReAct pairs? 
        # Actually ReAct is Triplet: Thought, Action, Observation.
        # Format in BaseAgent uses:
        # Step 1: Thought
        # Step 2: Action
        # Step 3: Observation
        
        # My step_count logic above:
        # Action 1 -> Step 1 (Thought), Step 2 (Action)
        # Tool End -> Step 3 (Observation)
        
        step_num = (self.step_count * 2) + 1
        
        # Truncate
        content = str(output)
        if len(content) > 500:
            content = content[:500] + "... [truncated]"

        self.queue.put_nowait({
            "type": "observation",
            "step": step_num,
            "agent": "coordinator",
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """Run on agent end."""
        # This is the final answer.
        pass
        
    from typing import Union

    def on_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any) -> Any:
        self.queue.put_nowait({
            "type": "error",
            "content": str(error)
        })
