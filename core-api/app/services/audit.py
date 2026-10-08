from typing import Any

from sqlalchemy.orm import Session

from app.models.activity import ActivityLog


def log_activity(
    db: Session,
    action: str,
    user_id: str,
    note_id: str | None = None,
    notebook_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    db.add(
        ActivityLog(
            action=action,
            user_id=user_id,
            note_id=note_id,
            notebook_id=notebook_id,
            metadata_=metadata or {},
        )
    )
