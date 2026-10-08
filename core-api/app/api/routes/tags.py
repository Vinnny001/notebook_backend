from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagRead

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagRead])
def list_tags(user: CurrentUser, db: DbSession) -> list[Tag]:
    return list(db.scalars(select(Tag).where(Tag.user_id == user.id).order_by(Tag.name)))


@router.post("", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(payload: TagCreate, user: CurrentUser, db: DbSession) -> Tag:
    existing = db.scalar(select(Tag).where(Tag.user_id == user.id, Tag.name == payload.name))
    if existing:
        raise HTTPException(status_code=409, detail={"code": "tag_exists"})
    tag = Tag(user_id=user.id, **payload.model_dump())
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag
