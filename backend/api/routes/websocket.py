from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.services.websocket_manager import WebSocketManager
from backend.services.react_orchestrator import ReActOrchestrator
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

manager = WebSocketManager()
orchestrator = ReActOrchestrator()

@router.websocket("/ws/analyze/{connection_id}")
async def websocket_analyze(websocket: WebSocket, connection_id: str):
    """
    WebSocket endpoint for streaming analysis steps.
    Client sends transaction JSON, Server streams steps back.
    """
    await websocket.accept()
    await manager.connect(websocket, connection_id)
    
    try:
        while True:
            # Wait for client to send transaction data
            data = await websocket.receive_text()
            transaction_data = json.loads(data)
            
            # Run analysis and stream results
            # Note: Since our orchestrator.run is blocking, we wrap it 
            # or use the placeholder stream generator we defined.
            # Ideally this happens in a separate thread/task to not block WS heartbeat.
            
            # For this demo, we'll iterate the generator
            async for step in orchestrator.stream(transaction_data):
                await manager.send_to_connection(connection_id, step)
                
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.send_to_connection(connection_id, {"error": str(e)})
        manager.disconnect(connection_id)
