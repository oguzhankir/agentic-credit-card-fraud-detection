import logging
import datetime
from langchain_core.callbacks import AsyncCallbackHandler
from typing import Any, Dict, List, Optional
from backend.services.websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)

class WebSocketCallbackHandler(AsyncCallbackHandler):
    """Callback handler that streams events to a WebSocket with timing and agent context"""
    
    def __init__(self, ws_manager: WebSocketManager, connection_id: str):
        self.ws_manager = ws_manager
        self.connection_id = connection_id
        self.current_agent = "coordinator"
        
    def set_agent(self, agent_name: str):
        """Allow agents to identify themselves before calling tools"""
        self.current_agent = agent_name

    async def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Run when chain starts running."""
        pass

    async def _send_step(self, step_type: str, content: str, metadata: Optional[Dict] = None):
        """Helper to send a formatted ReAct step"""
        await self.ws_manager.send_to_connection(self.connection_id, {
            "type": "react_step",
            "data": {
                "type": step_type,
                "agent": self.current_agent,
                "content": content,
                "timestamp": datetime.datetime.now().isoformat(),
                "metadata": metadata or {}
            }
        })

    async def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        """Run when tool starts running."""
        logger.info(f"🔧 WebSocket Callback triggered for {self.current_agent}")
        tool_name = serialized.get('name', 'unknown_tool')
        await self._send_step(
            "ACTION",
            f"Using tool: {tool_name}",
            {"tool": tool_name, "input": input_str}
        )

    async def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Run when tool ends running."""
        await self._send_step(
            "OBSERVATION",
            str(output)
        )
        
    async def on_agent_action(self, action: Any, **kwargs: Any) -> Any:
        """Run on agent action (Thought)."""
        await self._send_step(
            "THOUGHT",
            action.log,
            {"tool": action.tool, "tool_input": action.tool_input, "llm_used": True, "llm_purpose": "Reasoning"}
        )

    async def on_agent_finish(self, finish: Any, **kwargs: Any) -> None:
        """Run on agent end."""
        pass
