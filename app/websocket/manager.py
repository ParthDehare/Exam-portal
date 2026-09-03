import json
import asyncio
import redis.asyncio as redis
from fastapi import WebSocket
from typing import Dict, List
import logging
from config import settings

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self, redis_url: str = settings.redis_url):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.redis = redis.from_url(redis_url)
        self.pubsub = self.redis.pubsub()
        self._listener_task = None

    async def connect(self, websocket: WebSocket, room: int):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
            await self.pubsub.subscribe(f"room_{room}")
            if self._listener_task is None:
                self._listener_task = asyncio.create_task(self._listen())
        self.active_connections[room].append(websocket)

    def disconnect(self, websocket: WebSocket, room: int):
        if room in self.active_connections:
            if websocket in self.active_connections[room]:
                self.active_connections[room].remove(websocket)
            if not self.active_connections[room]:
                del self.active_connections[room]
                # Fire and forget unsubscribe
                asyncio.create_task(self.pubsub.unsubscribe(f"room_{room}"))

    async def broadcast(self, room: int, message: dict):
        # Publish event to Redis instead of sending locally
        await self.redis.publish(f"room_{room}", json.dumps(message))

    async def _listen(self):
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    channel = message["channel"].decode()
                    data = message["data"].decode()
                    room = int(channel.split("_")[1])
                    if room in self.active_connections:
                        for ws in self.active_connections[room]:
                            try:
                                await ws.send_text(data)
                            except Exception as e:
                                logger.error(f"WebSocket send failed: {e}")
        except Exception as e:
            logger.error(f"Redis pubsub error: {e}")

manager = ConnectionManager()
