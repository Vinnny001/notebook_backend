from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession
from app.models.attachment import Attachment
from app.models.note import Note, NoteVersion
from app.models.tag import Tag
from app.schemas.note import AttachmentCreate, AttachmentRead, NoteCreate, NoteRead, NoteUpdate, NoteVersionRead
from app.services.audit import log_activity
from app.services.events import publisher

router = APIRouter(prefix="/notes", tags=["notes"])


def owned_note(db: DbSession, note_id: str, user_id: str) -> Note:
    note = db.scalar(select(Note).options(selectinload(Note.tags)).where(Note.id == note_id))
    if note is None or note.user_id != user_id:
        raise HTTPException(status_code=404, detail={"code": "note_not_found"})
    return note


def sync_tags(db: DbSession, note: Note, user_id: str, tag_ids: list[str]) -> None:
    if not tag_ids:
        note.tags = []
        return
    tags = list(db.scalars(select(Tag).where(Tag.user_id == user_id, Tag.id.in_(tag_ids))))
    if len(tags) != len(set(tag_ids)):
        raise HTTPException(status_code=400, detail={"code": "invalid_tag_ids"})
    note.tags = tags


@router.get("", response_model=list[NoteRead])
def list_notes(
    user: CurrentUser,
    db: DbSession,
    q: str | None = None,
    notebook_id: str | None = None,
    archived: bool = False,
    deleted: bool = False,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[Note]:
    stmt = (
        select(Note)
        .options(selectinload(Note.tags))
        .where(Note.user_id == user.id, Note.is_archived == archived, Note.is_deleted == deleted)
        .order_by(Note.is_pinned.desc(), Note.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    if notebook_id:
        stmt = stmt.where(Note.notebook_id == notebook_id)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Note.title.ilike(like), Note.plain_text.ilike(like)))
    return list(db.scalars(stmt))


@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteCreate, user: CurrentUser, db: DbSession) -> Note:
    data = payload.model_dump(exclude={"tag_ids"})
    note = Note(user_id=user.id, **data)
    sync_tags(db, note, user.id, payload.tag_ids)
    db.add(note)
    log_activity(db, "note.created", user.id, note_id=note.id, notebook_id=note.notebook_id)
    db.commit()
    db.refresh(note)
    publisher.publish("note.created", {"note_id": note.id, "user_id": user.id})
    return owned_note(db, note.id, user.id)


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: str, user: CurrentUser, db: DbSession) -> Note:
    return owned_note(db, note_id, user.id)


@router.patch("/{note_id}", response_model=NoteRead)
def update_note(note_id: str, payload: NoteUpdate, user: CurrentUser, db: DbSession) -> Note:
    note = owned_note(db, note_id, user.id)
    data = payload.model_dump(exclude_unset=True, exclude={"tag_ids"})

    if "content" in data or "plain_text" in data:
        db.add(NoteVersion(note_id=note.id, content=note.content, plain_text=note.plain_text, created_by=user.id))

    if data.get("is_deleted") is True and not note.is_deleted:
        note.deleted_at = datetime.now(UTC)
    if data.get("is_deleted") is False:
        note.deleted_at = None

    for key, value in data.items():
        setattr(note, key, value)
    if payload.tag_ids is not None:
        sync_tags(db, note, user.id, payload.tag_ids)

    log_activity(db, "note.updated", user.id, note_id=note.id, notebook_id=note.notebook_id)
    db.commit()
    db.refresh(note)
    publisher.publish("note.updated", {"note_id": note.id, "user_id": user.id})
    return owned_note(db, note.id, user.id)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: str, user: CurrentUser, db: DbSession) -> None:
    note = owned_note(db, note_id, user.id)
    note.is_deleted = True
    note.deleted_at = datetime.now(UTC)
    log_activity(db, "note.deleted", user.id, note_id=note.id, notebook_id=note.notebook_id)
    db.commit()
    publisher.publish("note.deleted", {"note_id": note.id, "user_id": user.id})
    return None


@router.get("/{note_id}/versions", response_model=list[NoteVersionRead])
def list_versions(note_id: str, user: CurrentUser, db: DbSession) -> list[NoteVersion]:
    owned_note(db, note_id, user.id)
    return list(db.scalars(select(NoteVersion).where(NoteVersion.note_id == note_id).order_by(NoteVersion.created_at.desc())))


@router.post("/{note_id}/versions/{version_id}/restore", response_model=NoteRead)
def restore_version(note_id: str, version_id: str, user: CurrentUser, db: DbSession) -> Note:
    note = owned_note(db, note_id, user.id)
    version = db.get(NoteVersion, version_id)
    if version is None or version.note_id != note.id:
        raise HTTPException(status_code=404, detail={"code": "version_not_found"})
    db.add(NoteVersion(note_id=note.id, content=note.content, plain_text=note.plain_text, created_by=user.id))
    note.content = version.content
    note.plain_text = version.plain_text
    log_activity(db, "note.version_restored", user.id, note_id=note.id, notebook_id=note.notebook_id)
    db.commit()
    db.refresh(note)
    publisher.publish("note.updated", {"note_id": note.id, "user_id": user.id})
    return owned_note(db, note.id, user.id)


@router.post("/{note_id}/attachments", response_model=AttachmentRead, status_code=status.HTTP_201_CREATED)
def create_attachment(note_id: str, payload: AttachmentCreate, user: CurrentUser, db: DbSession) -> Attachment:
    note = owned_note(db, note_id, user.id)
    attachment = Attachment(note_id=note.id, uploaded_by=user.id, **payload.model_dump())
    db.add(attachment)
    log_activity(db, "attachment.created", user.id, note_id=note.id, notebook_id=note.notebook_id)
    db.commit()
    db.refresh(attachment)
    publisher.publish("attachment.created", {"note_id": note.id, "attachment_id": attachment.id, "user_id": user.id})
    return attachment
