# DownPlay

Video downloader for YouTube, TikTok, Instagram, Facebook, and X.

## Stack

- **Frontend**: Vue 3 + Vite
- **Backend**: FastAPI + yt-dlp

## Requirements

- Node.js 18+
- Python 3.10+
- FFmpeg

## Setup

```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

## Usage

```bash
# Terminal 1 — Backend (port 8000)
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload

# Terminal 2 — Frontend (port 5173)
cd frontend
npm run dev
```

Open `http://localhost:5173`.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | Backend API URL |

## Structure

```
backend/          FastAPI REST API
frontend/         Vue 3 + Vite UI
```
