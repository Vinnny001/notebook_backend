from datetime import datetime

from pydantic import BaseModel, Field


class NotebookCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    parent_id: str | None = None
    position: int = 0


class NotebookUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    parent_id: str | None = None
    position: int | None = None


class NotebookRead(BaseModel):
    id: str
    user_id: str
    parent_id: str | None
    name: str
    position: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
