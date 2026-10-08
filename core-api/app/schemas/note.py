from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.tag import TagRead


class NoteCreate(BaseModel):
    notebook_id: str | None = None
    title: str = Field(min_length=1, max_length=240)
    content: dict[str, Any] = Field(default_factory=dict)
    plain_text: str = ""
    tag_ids: list[str] = Field(default_factory=list)


class NoteUpdate(BaseModel):
    notebook_id: str | None = None
    title: str | None = Field(default=None, min_length=1, max_length=240)
    content: dict[str, Any] | None = None
    plain_text: str | None = None
    is_pinned: bool | None = None
    is_archived: bool | None = None
    is_deleted: bool | None = None
    tag_ids: list[str] | None = None


class NoteRead(BaseModel):
    id: str
    notebook_id: str | None
    user_id: str
    title: str
    content: dict[str, Any]
    plain_text: str
    is_pinned: bool
    is_archived: bool
    is_deleted: bool
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime
    tags: list[TagRead] = []

    model_config = {"from_attributes": True}


class NoteVersionRead(BaseModel):
    id: str
    note_id: str
    content: dict[str, Any]
    plain_text: str
    created_by: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AttachmentCreate(BaseModel):
    file_url: str
    file_type: str
    size: int = Field(ge=1)


class AttachmentRead(BaseModel):
    id: str
    note_id: str
    file_url: str
    file_type: str
    size: int
    uploaded_by: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
