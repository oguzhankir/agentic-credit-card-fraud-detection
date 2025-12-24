from typing import List, Dict
from fastapi import WebSocket
import logging
import json

logger = logging.getLogger(__name__)

class WebSocketManager:
    """
    Manages active WebSocket connections for real-time updates.
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, connection_id: str):
        """Accept connection and add to pool."""
        # await websocket.accept() # Handled in route usually
        self.active_connections[connection_id] = websocket
        logger.info(f"WebSocket client connected: {connection_id}")

    def disconnect(self, connection_id: str):
        """Remove connection from pool."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            logger.info(f"WebSocket client disconnected: {connection_id}")

    async def send_to_connection(self, connection_id: str, message: dict):
        """Send JSON message to specific client."""
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
                self.disconnect(connection_id)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        for connection_id in list(self.active_connections.keys()):
            await self.send_to_connection(connection_id, message)
