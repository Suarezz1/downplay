"""Application configuration and constants."""

import os
from pathlib import Path

# Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Cleanup
MAX_FILE_AGE_MINUTES = 30

# CORS
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

# Platform detection patterns
PLATFORM_PATTERNS = {
    "youtube": [
        r"(?:https?://)?(?:www\.)?youtube\.com/watch",
        r"(?:https?://)?(?:www\.)?youtube\.com/shorts",
        r"(?:https?://)?youtu\.be/",
        r"(?:https?://)?(?:www\.)?youtube\.com/embed",
    ],
    "tiktok": [
        r"(?:https?://)?(?:www\.)?tiktok\.com/@[\w.]+/video",
        r"(?:https?://)?vm\.tiktok\.com/",
        r"(?:https?://)?(?:www\.)?tiktok\.com/t/",
    ],
    "instagram": [
        r"(?:https?://)?(?:www\.)?instagram\.com/(?:p|reel|tv)/",
    ],
    "facebook": [
        r"(?:https?://)?(?:www\.)?facebook\.com/.+/videos/",
        r"(?:https?://)?(?:www\.)?facebook\.com/watch",
        r"(?:https?://)?fb\.watch/",
        r"(?:https?://)?(?:www\.)?facebook\.com/reel/",
    ],
    "x": [
        r"(?:https?://)?(?:www\.)?(?:twitter|x)\.com/.+/status/",
    ],
}

# Supported quality labels (ordered highest to lowest)
QUALITY_LABELS = ["2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"]
