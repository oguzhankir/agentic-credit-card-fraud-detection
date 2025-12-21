from langchain_core.callbacks import AsyncCallbackHandler
from typing import Any, Dict, List
from backend.services.websocket_manager import WebSocketManager
import logging

logger = logging.getLogger(__name__)

class WebSocketCallbackHandler(AsyncCallbackHandler):
    """Callback handler that streams events to a WebSocket"""
    
    def __init__(self, ws_manager: WebSocketManager, connection_id: str):
        self.ws_manager = ws_manager
        self.connection_id = connection_id
        
    async def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Run when chain starts running."""
        # Optional: Notify start
        pass

    async def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        """Run when tool starts running."""
        await self.ws_manager.send_to_connection(self.connection_id, {
            "type": "react_step",
            "data": {
                "type": "ACTION",
                "content": f"Starting tool: {serialized.get('name')}",
                "metadata": {"tool": serialized.get('name'), "input": input_str}
            }
        })

    async def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Run when tool ends running."""
        await self.ws_manager.send_to_connection(self.connection_id, {
            "type": "react_step",
            "data": {
                "type": "OBSERVATION",
                "content": str(output),
                "metadata": {}
            }
        })
        
    async def on_agent_action(self, action: Any, **kwargs: Any) -> Any:
        """Run on agent action."""
        # "Thought" is usually captured here or inferred
        await self.ws_manager.send_to_connection(self.connection_id, {
            "type": "react_step",
            "data": {
                "type": "THOUGHT",
                "content": action.log,
                "metadata": {"tool": action.tool, "tool_input": action.tool_input}
            }
        })

    async def on_agent_finish(self, finish: Any, **kwargs: Any) -> None:
        """Run on agent end."""
        pass
