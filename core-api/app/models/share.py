from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdMixin, utcnow


class Share(IdMixin, Base):
    __tablename__ = "shares"

    note_id: Mapped[str | None] = mapped_column(ForeignKey("notes.id", ondelete="CASCADE"))
    notebook_id: Mapped[str | None] = mapped_column(ForeignKey("notebooks.id", ondelete="CASCADE"))
    shared_with_user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    permission: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
