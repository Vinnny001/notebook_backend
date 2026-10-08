import json
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from fastapi import WebSocket


@dataclass
class Client:
    websocket: WebSocket
    user_id: str
    name: str | None = None
    color: str | None = None


class RoomManager:
    def __init__(self) -> None:
        self.rooms: dict[str, set[WebSocket]] = defaultdict(set)
        self.clients: dict[WebSocket, Client] = {}

    async def connect(self, note_id: str, websocket: WebSocket, user_id: str) -> None:
        await websocket.accept()
        self.rooms[note_id].add(websocket)
        self.clients[websocket] = Client(websocket=websocket, user_id=user_id)
        await self.broadcast_presence(note_id)

    async def disconnect(self, note_id: str, websocket: WebSocket) -> None:
        self.rooms[note_id].discard(websocket)
        self.clients.pop(websocket, None)
        if not self.rooms[note_id]:
            self.rooms.pop(note_id, None)
        else:
            await self.broadcast_presence(note_id)

    async def broadcast_json(self, note_id: str, message: dict[str, Any], sender: WebSocket | None = None) -> None:
        disconnected: list[WebSocket] = []
        for websocket in self.rooms.get(note_id, set()):
            if websocket is sender:
                continue
            try:
                await websocket.send_text(json.dumps(message))
            except RuntimeError:
                disconnected.append(websocket)
        for websocket in disconnected:
            await self.disconnect(note_id, websocket)

    async def broadcast_presence(self, note_id: str) -> None:
        users = [
            {"user_id": client.user_id, "name": client.name, "color": client.color}
            for websocket, client in self.clients.items()
            if websocket in self.rooms.get(note_id, set())
        ]
        await self.broadcast_json(note_id, {"type": "presence", "users": users})

    def update_client(self, websocket: WebSocket, name: str | None, color: str | None) -> None:
        client = self.clients.get(websocket)
        if client:
            client.name = name
            client.color = color
