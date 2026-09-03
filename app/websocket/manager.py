import json
from fastapi import WebSocket
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Maps room_id (int) to a list of active WebSocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: int):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
        self.active_connections[room].append(websocket)
        logger.info(f"WebSocket connected to room {room}. Total clients: {len(self.active_connections[room])}")

    def disconnect(self, websocket: WebSocket, room: int):
        if room in self.active_connections:
            if websocket in self.active_connections[room]:
                self.active_connections[room].remove(websocket)
            if not self.active_connections[room]:
                del self.active_connections[room]
            else:
                logger.info(f"WebSocket disconnected from room {room}. Remaining clients: {len(self.active_connections[room])}")

    async def broadcast(self, room: int, message: dict):
        if room in self.active_connections:
            data = json.dumps(message)
            for ws in self.active_connections[room]:
                try:
                    await ws.send_text(data)
                except Exception as e:
                    logger.error(f"WebSocket send failed: {e}")
                    # Optionally, you could remove the dead websocket here

manager = ConnectionManager()
