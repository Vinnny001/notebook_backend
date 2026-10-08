import json
from typing import Any

from redis import Redis

from app.core.config import settings


class EventPublisher:
    def __init__(self) -> None:
        self._redis: Redis | None = None

    def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        try:
            if self._redis is None:
                self._redis = Redis.from_url(settings.redis_url, decode_responses=True)
            self._redis.publish("notebook.events", json.dumps({"type": event_type, "payload": payload}))
        except Exception:
            # Event delivery should not make the core write path fail in local/dev mode.
            return


publisher = EventPublisher()
