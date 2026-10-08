from fastapi import APIRouter

from app.api.routes import auth, health, notebooks, notes, tags, users

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(notebooks.router)
api_router.include_router(notes.router)
api_router.include_router(tags.router)
