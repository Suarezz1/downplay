"""DownPlay API — FastAPI application entry point."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ALLOWED_ORIGINS, DOWNLOAD_DIR
from app.routes import health, video
from app.services.downloader import cleanup_old_files


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    # Startup: ensure download directory exists and clean old files
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    cleanup_old_files()

    # Start periodic cleanup task
    cleanup_task = asyncio.create_task(_periodic_cleanup())

    yield

    # Shutdown: cancel cleanup task
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


async def _periodic_cleanup():
    """Clean old files every 10 minutes."""
    while True:
        await asyncio.sleep(600)  # 10 minutes
        cleanup_old_files()


app = FastAPI(
    title="DownPlay API",
    description="Video downloader API supporting YouTube, TikTok, Instagram, Facebook, and X",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(video.router)
app.include_router(health.router)
