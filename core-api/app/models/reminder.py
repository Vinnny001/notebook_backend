from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdMixin


class Reminder(IdMixin, Base):
    __tablename__ = "reminders"

    note_id: Mapped[str] = mapped_column(ForeignKey("notes.id", ondelete="CASCADE"), index=True)
    checklist_item_id: Mapped[str | None] = mapped_column(String(120))
    remind_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    recurrence_rule: Mapped[str | None] = mapped_column(String(200))
    sent: Mapped[bool] = mapped_column(Boolean, default=False)
