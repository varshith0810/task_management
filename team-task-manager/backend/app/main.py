"""
Team Task Manager – FastAPI application factory.
Serves the React frontend as static files in production.
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import Base, engine


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


# ── App factory ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Full-stack Team Task Manager API.",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS – allow frontend dev server + production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API routes
    app.include_router(api_router)

    # Health check
    @app.get("/health", tags=["Health"])
    def health():
        return {"status": "ok", "version": settings.APP_VERSION}

    # Serve React frontend (static build) if it exists
    static_path = Path(__file__).parent.parent / "static"
    if static_path.exists():
        # Mount assets (JS/CSS bundles)
        assets_path = static_path / "assets"
        if assets_path.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")

        # Serve index.html for all non-API routes (SPA catch-all)
        index_file = static_path / "index.html"

        @app.get("/{full_path:path}", include_in_schema=False)
        def serve_spa(full_path: str):
            # Don't catch API routes
            if full_path.startswith("api/"):
                return JSONResponse({"detail": "Not found"}, status_code=404)
            # Serve static files if they exist
            file_path = static_path / full_path
            if file_path.exists() and file_path.is_file():
                return FileResponse(str(file_path))
            # Fall back to index.html for client-side routing
            return FileResponse(str(index_file))

    return app


app = create_app()
