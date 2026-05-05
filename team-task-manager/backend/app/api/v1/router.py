from fastapi import APIRouter
from app.api.v1.endpoints import auth, projects, tasks, dashboard
from app.api.v1.endpoints import users
api_router.include_router(users.router)
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(tasks.router)
api_router.include_router(dashboard.router)
