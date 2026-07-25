"""Health check endpoint."""

import shutil

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check():
    """Check server health and FFmpeg availability."""
    ffmpeg_path = shutil.which("ffmpeg")

    return {
        "status": "ok",
        "ffmpeg_available": ffmpeg_path is not None,
        "ffmpeg_path": ffmpeg_path,
    }
