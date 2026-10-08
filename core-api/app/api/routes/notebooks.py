from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.notebook import Notebook
from app.schemas.notebook import NotebookCreate, NotebookRead, NotebookUpdate
from app.services.audit import log_activity
from app.services.events import publisher

router = APIRouter(prefix="/notebooks", tags=["notebooks"])


@router.get("", response_model=list[NotebookRead])
def list_notebooks(user: CurrentUser, db: DbSession) -> list[Notebook]:
    return list(db.scalars(select(Notebook).where(Notebook.user_id == user.id).order_by(Notebook.position, Notebook.name)))


@router.post("", response_model=NotebookRead, status_code=status.HTTP_201_CREATED)
def create_notebook(payload: NotebookCreate, user: CurrentUser, db: DbSession) -> Notebook:
    notebook = Notebook(user_id=user.id, **payload.model_dump())
    db.add(notebook)
    log_activity(db, "notebook.created", user.id, notebook_id=notebook.id)
    db.commit()
    db.refresh(notebook)
    publisher.publish("notebook.created", {"notebook_id": notebook.id, "user_id": user.id})
    return notebook


@router.patch("/{notebook_id}", response_model=NotebookRead)
def update_notebook(notebook_id: str, payload: NotebookUpdate, user: CurrentUser, db: DbSession) -> Notebook:
    notebook = db.get(Notebook, notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=404, detail={"code": "notebook_not_found"})
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(notebook, key, value)
    log_activity(db, "notebook.updated", user.id, notebook_id=notebook.id)
    db.commit()
    db.refresh(notebook)
    publisher.publish("notebook.updated", {"notebook_id": notebook.id, "user_id": user.id})
    return notebook


@router.delete("/{notebook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notebook(notebook_id: str, user: CurrentUser, db: DbSession) -> None:
    notebook = db.get(Notebook, notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=404, detail={"code": "notebook_not_found"})
    db.delete(notebook)
    db.commit()
    publisher.publish("notebook.deleted", {"notebook_id": notebook_id, "user_id": user.id})
    return None
