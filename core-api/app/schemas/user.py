from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr


class UserRead(BaseModel):
    id: str
    email: EmailStr
    name: str
    avatar_url: str | None
    timezone: str
    role: str
    is_verified: bool
    email_preferences: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: str | None = None
    avatar_url: str | None = None
    timezone: str | None = None
    email_preferences: dict[str, Any] | None = None
