"""
Team Task Manager – FastAPI application factory.
"""
 
from contextlib import asynccontextmanager
 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
 
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import Base, engine
 
 
# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables (dev convenience; use Alembic for production)
    Base.metadata.create_all(bind=engine)
    yield
    # Nothing to teardown currently
 
 
# ── App factory ───────────────────────────────────────────────────────────────
 
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Full-stack Team Task Manager API. "
            "Role-based access control, project management, and task tracking."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
 
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
 
    # Routes
    app.include_router(api_router)
 
    return app
 
 
app = create_app()
 
 
# ── Health check (registered at module level so it is always reachable) ───────
 
@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "version": settings.APP_VERSION}
