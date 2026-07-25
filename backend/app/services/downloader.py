"""Video download service powered by yt-dlp."""

import logging
import re
import time
import uuid
import threading
from pathlib import Path

import yt_dlp

from app.config import DOWNLOAD_DIR, MAX_FILE_AGE_MINUTES, PLATFORM_PATTERNS

logger = logging.getLogger(__name__)

# In-memory job store (sufficient for personal use)
_jobs: dict[str, dict] = {}
_lock = threading.Lock()


def detect_platform(url: str) -> str:
    """Detect which platform a URL belongs to."""
    for platform, patterns in PLATFORM_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, url):
                return platform
    return "other"


def _strip_playlist(url: str) -> str:
    """Remove playlist parameters from URL to get single video."""
    # Remove &list=... and &index=... from YouTube URLs
    import urllib.parse
    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query)
    # Keep only the 'v' parameter for YouTube
    params.pop('list', None)
    params.pop('index', None)
    params.pop('start_radio', None)
    clean_query = urllib.parse.urlencode(params, doseq=True)
    return urllib.parse.urlunparse(parsed._replace(query=clean_query))


def get_video_info(url: str) -> dict:
    """Extract video metadata and available formats without downloading."""
    url = _strip_playlist(url)

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "no_color": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if not info:
        raise ValueError("Could not extract video information")

    # Parse formats into a clean structure
    formats = _parse_formats(info.get("formats", []))
    platform = detect_platform(url)

    # Safe integer cast for duration and view_count
    duration = info.get("duration")
    if duration is not None:
        try:
            duration = int(round(float(duration)))
        except (ValueError, TypeError):
            duration = None

    view_count = info.get("view_count")
    if view_count is not None:
        try:
            view_count = int(view_count)
        except (ValueError, TypeError):
            view_count = None

    return {
        "title": info.get("title", "Unknown"),
        "thumbnail": info.get("thumbnail"),
        "duration": duration,
        "platform": platform,
        "uploader": info.get("uploader") or info.get("channel"),
        "view_count": view_count,
        "formats": formats,
    }


def _parse_formats(raw_formats: list[dict]) -> list[dict]:
    """Parse yt-dlp formats into a clean, deduplicated list."""
    seen_qualities = set()
    parsed = []

    for fmt in raw_formats:
        format_id = fmt.get("format_id", "")
        ext = fmt.get("ext", "unknown")
        height = fmt.get("height")
        has_video = fmt.get("vcodec", "none") != "none"
        has_audio = fmt.get("acodec", "none") != "none"

        # Skip formats without useful content
        if not has_video and not has_audio:
            continue
        # Skip storyboard/manifest formats
        if ext in ("mhtml", "json"):
            continue

        # Build quality label
        if has_video and height:
            quality = f"{height}p"
        elif has_audio and not has_video:
            quality = "audio_only"
        else:
            quality = fmt.get("format_note", "unknown")

        # Deduplicate: keep best version of each quality
        dedup_key = f"{quality}_{ext}_{has_video}_{has_audio}"
        if dedup_key in seen_qualities:
            continue
        seen_qualities.add(dedup_key)

        # Build codec info
        vcodec = fmt.get("vcodec", "none")
        acodec = fmt.get("acodec", "none")
        codec_parts = []
        if has_video and vcodec != "none":
            codec_parts.append(vcodec.split(".")[0])
        if has_audio and acodec != "none":
            codec_parts.append(acodec.split(".")[0])
        codec = "+".join(codec_parts) if codec_parts else None

        # Safe integer cast for filesizes
        filesize = fmt.get("filesize")
        if filesize is not None:
            try:
                filesize = int(filesize)
            except (ValueError, TypeError):
                filesize = None

        filesize_approx = fmt.get("filesize_approx")
        if filesize_approx is not None:
            try:
                filesize_approx = int(filesize_approx)
            except (ValueError, TypeError):
                filesize_approx = None

        parsed.append(
            {
                "format_id": format_id,
                "ext": ext,
                "quality": quality,
                "resolution": fmt.get("resolution"),
                "filesize": filesize,
                "filesize_approx": filesize_approx,
                "has_audio": has_audio,
                "has_video": has_video,
                "codec": codec,
                "tbr": fmt.get("tbr"),
            }
        )

    # Sort: video formats by height desc, then audio
    def sort_key(f):
        if f["has_video"]:
            match = re.match(r"(\d+)p", f["quality"])
            return (0, -(int(match.group(1)) if match else 0))
        return (1, 0)

    parsed.sort(key=sort_key)
    return parsed


def start_download(url: str, format_id: str | None, audio_only: bool) -> str:
    """Start a download job and return the job ID."""
    job_id = str(uuid.uuid4())[:8]

    with _lock:
        _jobs[job_id] = {
            "status": "pending",
            "progress": 0.0,
            "filename": None,
            "error": None,
        }

    # Run download in a separate thread
    thread = threading.Thread(
        target=_download_worker,
        args=(job_id, url, format_id, audio_only),
        daemon=True,
    )
    thread.start()

    return job_id


def get_job_status(job_id: str) -> dict | None:
    """Get the current status of a download job."""
    with _lock:
        job = _jobs.get(job_id)
        if job:
            return {
                "job_id": job_id,
                **job,
            }
    return None


def get_file_path(job_id: str) -> Path | None:
    """Get the file path for a completed download."""
    with _lock:
        job = _jobs.get(job_id)
        if job and job["status"] == "completed" and job["filename"]:
            filepath = DOWNLOAD_DIR / job["filename"]
            if filepath.exists():
                return filepath
    return None


def _download_worker(
    job_id: str, url: str, format_id: str | None, audio_only: bool
) -> None:
    """Worker thread that performs the actual download."""
    # Strip playlist params from URL
    url = _strip_playlist(url)

    def progress_hook(d: dict) -> None:
        """Update job progress from yt-dlp callback."""
        with _lock:
            job = _jobs.get(job_id)
            if not job:
                return

            if d["status"] == "downloading":
                job["status"] = "downloading"
                # Try multiple ways to calculate progress
                total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                downloaded = d.get("downloaded_bytes", 0)
                if total > 0:
                    job["progress"] = min((downloaded / total) * 100, 99.0)
                else:
                    # Fallback: use fragment progress if available
                    frag_index = d.get("fragment_index", 0)
                    frag_count = d.get("fragment_count", 0)
                    if frag_count > 0:
                        job["progress"] = min((frag_index / frag_count) * 100, 99.0)
                    elif downloaded > 0:
                        # At least show something is happening
                        job["progress"] = min(job["progress"] + 0.5, 95.0)

                logger.info(
                    f"[{job_id}] Progress: {job['progress']:.1f}% "
                    f"(downloaded={downloaded}, total={total})"
                )
            elif d["status"] == "finished":
                job["status"] = "processing"
                job["progress"] = 99.0
                logger.info(f"[{job_id}] Download finished, processing...")

    # Build output template
    output_template = str(DOWNLOAD_DIR / f"{job_id}_%(title)s.%(ext)s")

    # Build format selection
    if audio_only:
        fmt = "bestaudio/best"
        postprocessors = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
    elif format_id:
        # Select specific format + best audio, with multiple fallbacks
        fmt = f"{format_id}+bestaudio/{format_id}/bestvideo+bestaudio/best"
        postprocessors = []
    else:
        fmt = "bestvideo+bestaudio/best"
        postprocessors = []

    ydl_opts = {
        "format": fmt,
        "outtmpl": output_template,
        "progress_hooks": [progress_hook],
        "postprocessors": postprocessors,
        "no_color": True,
        "noplaylist": True,
        "merge_output_format": "mp4" if not audio_only else None,
        # Avoid very long filenames
        "restrictfilenames": True,
    }

    # Remove None values
    ydl_opts = {k: v for k, v in ydl_opts.items() if v is not None}

    logger.info(f"[{job_id}] Starting download: url={url}, format={fmt}, audio_only={audio_only}")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        # Find the downloaded file
        downloaded_file = _find_downloaded_file(job_id)
        logger.info(f"[{job_id}] Looking for file with prefix '{job_id}' in {DOWNLOAD_DIR}")

        with _lock:
            job = _jobs.get(job_id)
            if job:
                if downloaded_file:
                    job["status"] = "completed"
                    job["progress"] = 100.0
                    job["filename"] = downloaded_file.name
                    logger.info(f"[{job_id}] Completed: {downloaded_file.name}")
                else:
                    # List what files we actually have
                    files = list(DOWNLOAD_DIR.iterdir())
                    logger.error(f"[{job_id}] File not found. Files in dir: {[f.name for f in files]}")
                    job["status"] = "failed"
                    job["error"] = "Download completed but file not found"

    except Exception as e:
        logger.error(f"[{job_id}] Download failed: {e}")
        with _lock:
            job = _jobs.get(job_id)
            if job:
                job["status"] = "failed"
                job["error"] = str(e)[:500]


def _find_downloaded_file(job_id: str) -> Path | None:
    """Find the file downloaded for a given job ID."""
    for filepath in DOWNLOAD_DIR.iterdir():
        if filepath.name.startswith(job_id) and filepath.is_file():
            return filepath
    return None


def cleanup_old_files() -> int:
    """Remove files older than MAX_FILE_AGE_MINUTES. Returns count removed."""
    removed = 0
    now = time.time()
    max_age_seconds = MAX_FILE_AGE_MINUTES * 60

    for filepath in DOWNLOAD_DIR.iterdir():
        if filepath.is_file():
            age = now - filepath.stat().st_mtime
            if age > max_age_seconds:
                filepath.unlink(missing_ok=True)
                removed += 1

    # Also clean up completed/failed jobs from memory
    with _lock:
        stale_ids = [
            jid
            for jid, job in _jobs.items()
            if job["status"] in ("completed", "failed")
            and not (job.get("filename") and (DOWNLOAD_DIR / job["filename"]).exists())
        ]
        for jid in stale_ids:
            del _jobs[jid]

    return removed
