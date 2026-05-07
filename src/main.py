#!/usr/bin/env python3
"""
Web Interface for MTV Downloader
A lightweight web interface for the MediathekView Downloader with Python backend
supporting concurrent web requests and downloads.
"""

import asyncio
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from starlette.background import BackgroundTask

# Add the source directory to Python path to import mtv_dl module
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the mtv_dl functionality
try:
    from mtv_dl.mtv_dl import Database, Downloader
except ImportError as e:
    print(f"Failed to import mtv_dl: {e}")
    raise

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MTV Downloader Web Interface",
    description="A lightweight web interface for downloading videos from German public broadcasting services",
    version="1.0.0",
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
frontend_dir = Path(__file__).parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Global variables for managing downloads
download_queue = []
executor = ThreadPoolExecutor(max_workers=4)
active_downloads = {}


# Pydantic models for API requests and responses
class DownloadRequest(BaseModel):
    filters: List[str]
    quality: str = "url_http"
    target_directory: str = "./downloads"
    include_subtitles: bool = True
    include_nfo: bool = True
    merge_to_mkv: bool = False


class DownloadStatus(BaseModel):
    id: str
    status: str
    progress: float
    message: str
    file_path: Optional[str] = None


class ShowItem(BaseModel):
    hash: str
    channel: str
    title: str
    topic: str
    size: int
    start: str
    duration: str
    age: str
    region: str
    downloaded: Optional[str] = None


class SearchFilters(BaseModel):
    filters: List[str]


# Initialize database connection
DATABASE_DIR = Path.home() / ".mtv_dl_web"
DATABASE_DIR.mkdir(exist_ok=True)
DATABASE_FILE = DATABASE_DIR / "filmliste.sqlite"
HISTORY_FILE = DATABASE_DIR / "history.sqlite"

try:
    db = Database(DATABASE_FILE, HISTORY_FILE)
    db.update_if_old()  # Ensure database is up to date
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    raise


# API Routes
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    try:
        with open(frontend_dir / "index.html", "r") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "<h1>MTV Downloader Web Interface</h1><p>Frontend not found</p>"


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/search")
async def search_shows(filters: SearchFilters):
    """
    Search for shows based on filters
    """
    try:
        shows = list(db.filtered(filters.filters))
        return {"results": [ShowItem(**show) for show in shows]}
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/download")
async def start_download(
    download_request: DownloadRequest, background_tasks: BackgroundTasks
):
    """
    Start downloading shows based on filters
    """
    try:
        # Validate target directory
        target_path = Path(download_request.target_directory)
        target_path.mkdir(parents=True, exist_ok=True)

        # Get filtered shows
        shows = list(db.filtered(download_request.filters))

        if not shows:
            raise HTTPException(
                status_code=404, detail="No shows found matching filters"
            )

        # Process each show in the background
        download_ids = []
        for show in shows:
            show_id = show["hash"]
            download_ids.append(show_id)

            # Add to active downloads
            active_downloads[show_id] = {
                "status": "queued",
                "progress": 0.0,
                "message": "Queued for download",
                "file_path": None,
            }

            # Submit download task to background
            background_tasks.add_task(download_show_background, show, download_request)

        return {
            "message": f"Started downloading {len(shows)} shows",
            "download_ids": download_ids,
        }

    except Exception as e:
        logger.error(f"Download start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def download_show_background(show_data: dict, download_request: DownloadRequest):
    """
    Background task to handle the actual download
    """
    try:
        show_id = show_data["hash"]

        # Update status
        active_downloads[show_id]["status"] = "downloading"
        active_downloads[show_id]["message"] = "Starting download..."

        # Create downloader instance
        downloader = Downloader(show_data)

        # Determine quality
        quality_map = {
            "low": ("url_http_small", "url_http", "url_http_hd"),
            "medium": ("url_http", "url_http_small", "url_http_hd"),
            "high": ("url_http_hd", "url_http", "url_http_small"),
        }
        quality = quality_map.get(
            download_request.quality, ("url_http", "url_http_small", "url_http_hd")
        )

        # Perform download
        path = downloader.download(
            quality=quality,
            target=Path(download_request.target_directory),
            include_subtitles=download_request.include_subtitles,
            include_nfo=download_request.include_nfo,
            merge_to_mkv=download_request.merge_to_mkv,
        )

        # Update status
        if path:
            active_downloads[show_id]["status"] = "completed"
            active_downloads[show_id]["message"] = "Download completed"
            active_downloads[show_id]["file_path"] = str(path)
        else:
            active_downloads[show_id]["status"] = "failed"
            active_downloads[show_id]["message"] = "Download failed"

    except Exception as e:
        logger.error(f"Background download failed for {show_data['hash']}: {e}")
        active_downloads[show_id]["status"] = "failed"
        active_downloads[show_id]["message"] = f"Download failed: {str(e)}"


@app.get("/api/download/status/{download_id}")
async def get_download_status(download_id: str):
    """
    Get the status of a specific download
    """
    if download_id not in active_downloads:
        raise HTTPException(status_code=404, detail="Download not found")

    return active_downloads[download_id]


@app.get("/api/download/status")
async def get_all_download_statuses():
    """
    Get statuses of all active downloads
    """
    return active_downloads


if __name__ == "__main__":
    import uvicorn

    # For development purposes
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
