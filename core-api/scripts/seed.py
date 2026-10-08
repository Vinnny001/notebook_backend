from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.notebook import Notebook
from app.models.note import Note
from app.models.tag import Tag
from app.models.user import User


def seed(db: Session) -> None:
    user = db.query(User).filter(User.email == "demo@example.com").first()
    if user is None:
        user = User(email="demo@example.com", hashed_password=hash_password("password123"), name="Demo User", timezone="UTC", is_verified=True)
        db.add(user)
        db.flush()

    notebook = db.query(Notebook).filter(Notebook.user_id == user.id, Notebook.name == "Product").first()
    if notebook is None:
        notebook = Notebook(user_id=user.id, name="Product", position=0)
        db.add(notebook)
        db.flush()

    tag = db.query(Tag).filter(Tag.user_id == user.id, Tag.name == "planning").first()
    if tag is None:
        tag = Tag(user_id=user.id, name="planning", color="#0f766e")
        db.add(tag)
        db.flush()

    note = db.query(Note).filter(Note.user_id == user.id, Note.title == "Launch checklist").first()
    if note is None:
        note = Note(
            user_id=user.id,
            notebook_id=notebook.id,
            title="Launch checklist",
            content={
                "type": "doc",
                "content": [
                    {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "Launch checklist"}]},
                    {"type": "paragraph", "content": [{"type": "text", "text": "Invite collaborators, verify search, and test autosave."}]},
                ],
            },
            plain_text="Launch checklist\nInvite collaborators, verify search, and test autosave.",
            is_pinned=True,
        )
        note.tags = [tag]
        db.add(note)

    db.commit()


if __name__ == "__main__":
    with SessionLocal() as session:
        seed(session)
    print("Seeded demo@example.com / password123")
