from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdMixin, TimestampMixin


class Notebook(IdMixin, TimestampMixin, Base):
    __tablename__ = "notebooks"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("notebooks.id", ondelete="SET NULL"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    position: Mapped[int] = mapped_column(Integer, default=0)

    user = relationship("User", back_populates="notebooks")
    parent = relationship("Notebook", remote_side="Notebook.id")
    notes = relationship("Note", back_populates="notebook")
