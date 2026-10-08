import json

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect

from app.auth import validate_access_token
from app.config import settings
from app.rooms import RoomManager

app = FastAPI(title=settings.app_name)
rooms = RoomManager()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ready"}


@app.websocket("/ws/notes/{note_id}")
async def note_socket(websocket: WebSocket, note_id: str, token: str = Query()) -> None:
    try:
        user_id = validate_access_token(token)
    except ValueError:
        await websocket.close(code=4401)
        return

    await rooms.connect(note_id, websocket, user_id)
    try:
        while True:
            raw = await websocket.receive_text()
            message = json.loads(raw)
            message_type = message.get("type")

            if message_type == "presence:update":
                rooms.update_client(websocket, message.get("name"), message.get("color"))
                await rooms.broadcast_presence(note_id)
                continue

            if message_type in {"yjs:update", "cursor:update", "typing:update"}:
                await rooms.broadcast_json(
                    note_id,
                    {"type": message_type, "note_id": note_id, "user_id": user_id, "payload": message.get("payload")},
                    sender=websocket,
                )
                continue

            await websocket.send_text(json.dumps({"type": "error", "code": "unsupported_message"}))
    except WebSocketDisconnect:
        await rooms.disconnect(note_id, websocket)
    except json.JSONDecodeError:
        await websocket.send_text(json.dumps({"type": "error", "code": "invalid_json"}))
        await rooms.disconnect(note_id, websocket)
