"""Video-related API endpoints."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import (
    DownloadRequest,
    DownloadStatus,
    VideoInfoRequest,
    VideoInfoResponse,
)
from app.services import downloader

router = APIRouter(prefix="/api/video", tags=["video"])


@router.post("/info", response_model=VideoInfoResponse)
async def get_video_info(request: VideoInfoRequest):
    """Extract video metadata and available formats from a URL."""
    try:
        info = downloader.get_video_info(str(request.url))
        return VideoInfoResponse(**info)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not extract video info: {e}",
        )


@router.post("/download")
async def start_download(request: DownloadRequest):
    """Start a video download job."""
    try:
        job_id = downloader.start_download(
            url=str(request.url),
            format_id=request.format_id,
            audio_only=request.audio_only,
        )
        return {"job_id": job_id, "status": "pending"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not start download: {e}",
        )


@router.get("/status/{job_id}", response_model=DownloadStatus)
async def get_download_status(job_id: str):
    """Check the status and progress of a download job."""
    status = downloader.get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return DownloadStatus(**status)


@router.get("/file/{job_id}")
async def download_file(job_id: str):
    """Download the completed file."""
    filepath = downloader.get_file_path(job_id)
    if not filepath:
        raise HTTPException(status_code=404, detail="File not found or not ready")

    # Determine content type
    ext = filepath.suffix.lower()
    content_types = {
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".mkv": "video/x-matroska",
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".ogg": "audio/ogg",
        ".wav": "audio/wav",
    }
    content_type = content_types.get(ext, "application/octet-stream")

    # Clean filename for download (remove job_id prefix)
    clean_name = filepath.name
    if clean_name.startswith(f"{job_id}_"):
        clean_name = clean_name[len(job_id) + 1 :]

    def file_iterator():
        with open(filepath, "rb") as f:
            while chunk := f.read(1024 * 1024):  # 1MB chunks
                yield chunk

    return StreamingResponse(
        file_iterator(),
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{clean_name}"',
            "Content-Length": str(filepath.stat().st_size),
        },
    )
