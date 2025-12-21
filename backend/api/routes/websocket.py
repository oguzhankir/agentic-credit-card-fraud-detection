from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
import json
import logging

router = APIRouter(tags=["websocket"]) # No prefix typically for WS, or /ws

from uuid import uuid4

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Accept connection
    if not hasattr(websocket.app.state, 'ws_manager'):
        await websocket.close()
        return

    ws_manager = websocket.app.state.ws_manager
    connection_id = str(uuid4())
    await ws_manager.connect(websocket, connection_id)
    
    try:
        while True:
            # Receive message
            text = await websocket.receive_text()
            data = json.loads(text)
            
            if data.get('action') == 'analyze':
                # Stream analysis
                transaction = data.get('transaction')
                if transaction:
                    await ws_manager.stream_react_steps(connection_id, transaction)
            
            elif data.get('action') == 'ping':
                # Heartbeat
                await ws_manager.send_to_connection(connection_id, {
                    'type': 'heartbeat',
                    'timestamp': datetime.now().isoformat()
                })
                
    except WebSocketDisconnect:
        ws_manager.disconnect(connection_id)
    except Exception as e:
        logging.error(f"WS Error: {e}")
        ws_manager.disconnect(connection_id)
