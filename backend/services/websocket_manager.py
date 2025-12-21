from fastapi import WebSocket
from typing import List, Dict
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, connection_id: str):
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        logger.info(f"WS Client connected: {connection_id}")
        
        await self.send_to_connection(connection_id, {
            'type': 'connected',
            'connection_id': connection_id,
            'timestamp': datetime.now().isoformat()
        })

    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            logger.info(f"WS Client disconnected: {connection_id}")

    async def send_to_connection(self, connection_id: str, message: dict):
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to {connection_id}: {e}")
                self.disconnect(connection_id)

    async def broadcast(self, message: dict):
        for cid in list(self.active_connections.keys()):
            await self.send_to_connection(cid, message)

    async def stream_react_steps(self, connection_id: str, transaction: dict):
        """
        Runs the ReAct engine and streams each step to the client.
        """
        from backend.services.react_engine import ReActEngine
        engine = ReActEngine()
        
        # Default mock history if none
        history = transaction.get('customer_history', {
            "avg_amount": 100, "std_amount": 20, "usual_hours": [12, 18], "transaction_count": 50
        })
        
        try:
            for step in engine.stream_analysis(transaction, history):
                await self.send_to_connection(connection_id, step)
                import asyncio
                await asyncio.sleep(0.5) # Forced delay for visual impact
        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            await self.send_to_connection(connection_id, {
                "type": "error",
                "message": str(e)
            })
