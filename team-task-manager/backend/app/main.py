"""
Team Task Manager – FastAPI application factory.
"""
 
from contextlib import asynccontextmanager
from pathlib import Path
 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
 
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import Base, engine
 
 
# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
 
 
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
 
    # API Routes
    app.include_router(api_router)
 
    # Health check
    @app.get("/health", tags=["Health"])
    def health():
        return {"status": "ok", "version": settings.APP_VERSION}
 
    # Serve React frontend static files
    static_path = Path(__file__).parent / "static"
    if static_path.exists():
        app.mount("/assets", StaticFiles(directory=str(static_path / "assets")), name="assets")
 
        # Catch-all: serve index.html for all non-API routes (React Router)
        @app.get("/{full_path:path}")
        async def serve_frontend(full_path: str):
            index = static_path / "index.html"
            return FileResponse(str(index))
 
    return app
 
 
app = create_app()
