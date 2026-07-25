"""Pydantic models for request/response validation."""

from pydantic import BaseModel, HttpUrl


class VideoInfoRequest(BaseModel):
    """Request body to extract video information."""

    url: HttpUrl


class VideoFormat(BaseModel):
    """A single available format for a video."""

    format_id: str
    ext: str
    quality: str  # "1080p", "720p", "audio_only", etc.
    resolution: str | None = None  # "1920x1080"
    filesize: int | None = None  # bytes
    filesize_approx: int | None = None
    has_audio: bool = True
    has_video: bool = True
    codec: str | None = None
    tbr: float | None = None  # total bitrate


class VideoInfoResponse(BaseModel):
    """Response with video metadata and available formats."""

    title: str
    thumbnail: str | None = None
    duration: int | None = None  # seconds
    platform: str  # "youtube", "tiktok", etc.
    uploader: str | None = None
    view_count: int | None = None
    formats: list[VideoFormat] = []


class DownloadRequest(BaseModel):
    """Request body to start a download."""

    url: HttpUrl
    format_id: str | None = None  # None = best quality
    audio_only: bool = False


class DownloadStatus(BaseModel):
    """Status of an ongoing or completed download."""

    job_id: str
    status: str  # "pending", "downloading", "processing", "completed", "failed"
    progress: float = 0.0  # 0.0 - 100.0
    filename: str | None = None
    error: str | None = None
