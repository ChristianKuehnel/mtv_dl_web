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
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add the bundled mtv_dl directory to Python path to import mtv_dl module
sys.path.insert(0, str(Path(__file__).parent.parent / "mtv_dl" / "src"))

# Import the mtv_dl functionality
try:
    from mtv_dl.mtv_dl import Database, Downloader
except ImportError as e:
    print(f"Failed to import mtv_dl: {e}")
    raise

# Configure logging
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
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
download_queue: list[dict[str, Any]] = []
executor = ThreadPoolExecutor(max_workers=4)
active_downloads: dict[str, dict[str, Any]] = {}


# Pydantic models for API requests and responses
class DownloadRequest(BaseModel):
    filters: list[str]
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
    file_path: str | None = None


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
    downloaded: str | None = None


class SearchFilters(BaseModel):
    filters: list[str]


# Supported filter operators and fields for validation
SUPPORTED_OPERATORS = {"=", "!=", "+", "-"}
SUPPORTED_FIELDS = {
    "description",
    "region",
    "size",
    "channel",
    "topic",
    "title",
    "hash",
    "url_http",
    "duration",
    "age",
    "start",
    "dow",
    "hour",
    "minute",
    "season",
    "episode",
}


def validate_filters(filters: list[str]) -> None:
    """
    Validate that filters use supported operators and fields

    Args:
        filters: List of filter strings to validate

    Raises:
        HTTPException: 400 Bad Request if invalid operators or fields are found
    """
    import re

    for filter_str in filters:
        # Parse filter string using the same regex as mtv_dl
        match = re.match(
            r"^(?P<field>\w+)(?P<operator>(?:=|!=|\+|-|\W+))(?P<pattern>.*)$",
            filter_str,
        )
        if not match:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid filter format: '{filter_str}'. Expected format: field<operator>value (e.g., channel=ARD, title+News)",
            )

        field = match.group("field")
        operator = match.group("operator")

        # Replace url with url_http for validation (same as mtv_dl does)
        if field == "url":
            field = "url_http"

        # Validate operator
        if operator not in SUPPORTED_OPERATORS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported operator '{operator}' in filter: '{filter_str}'. "
                f"Supported operators: {', '.join(sorted(SUPPORTED_OPERATORS))}",
            )

        # Validate field
        if field not in SUPPORTED_FIELDS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported field '{field}' in filter: '{filter_str}'. "
                f"Supported fields: {', '.join(sorted(SUPPORTED_FIELDS))}",
            )


# Database configuration
DATABASE_DIR = Path(os.environ.get("DATABASE_DIR", str(Path.home() / ".mtv_dl_web"))).expanduser()
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_FILE = DATABASE_DIR / "filmliste.sqlite"
HISTORY_FILE = DATABASE_DIR / "history.sqlite"


def get_db_connection():
    """
    Create a new database connection for each request to avoid thread-safety issues
    """
    try:
        db = Database(DATABASE_FILE, HISTORY_FILE)
        if os.environ.get("MTV_DL_WEB_SKIP_DB_UPDATE") != "1":
            db.update_if_old()  # Ensure database is up to date
        logger.debug("Database connection created successfully")
        return db
    except Exception as e:
        logger.error(f"Failed to create database connection: {e}")
        raise


# API Routes
@app.get("/", response_class=HTMLResponse)
async def read_root() -> str:
    """Serve the main HTML page"""
    try:
        with open(frontend_dir / "index.html", "r") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "<h1>Hello World</h1><p>MTV Downloader Web Interface</p>"


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint that verifies service readiness

    Returns:
        JSON: { "status": "healthy" } or { "status": "unhealthy" }
    """
    import time

    start_time = time.time()

    # Initialize response
    response = {"status": "healthy"}

    try:
        # Check database connectivity by creating a new connection
        try:
            db_conn = get_db_connection()
            # Use a simple query to validate connectivity
            with db_conn.connection:
                cursor = db_conn.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            response["status"] = "unhealthy"
            return response
    except Exception as e:
        logger.error(f"Database health check error: {e}")
        response["status"] = "unhealthy"
        return response

    # Calculate response time
    response_time_ms = round((time.time() - start_time) * 1000, 2)

    # Log health check (sanitized)
    logger.info(f"Health check: {response['status']}, response time: {response_time_ms}ms")

    # Enforce 500ms threshold (fail if exceeded)
    if response_time_ms > 500:
        logger.warning(f"Health check response time {response_time_ms}ms exceeds 500ms threshold")
        response["status"] = "unhealthy"

    return response


@app.post("/api/search")
async def search_shows(filters: SearchFilters) -> dict[str, list[ShowItem]]:
    """
    Search for shows based on filters

    Validates filter operators and fields before processing the search.
    """
    try:
        # Validate filters before processing
        validate_filters(filters.filters)

        # Perform the search using a fresh database connection
        db_conn = get_db_connection()
        shows = list(db_conn.filtered(filters.filters))
        
        # Convert datetime and timedelta objects to strings for Pydantic validation
        results = []
        for show in shows:
            show_dict = dict(show)
            # Convert datetime objects to ISO format strings
            if isinstance(show_dict.get('start'), datetime):
                show_dict['start'] = show_dict['start'].isoformat()
            if isinstance(show_dict.get('downloaded'), datetime):
                show_dict['downloaded'] = show_dict['downloaded'].isoformat()
            # Convert timedelta objects to string representation
            if isinstance(show_dict.get('duration'), timedelta):
                show_dict['duration'] = str(show_dict['duration'])
            if isinstance(show_dict.get('age'), timedelta):
                show_dict['age'] = str(show_dict['age'])
            results.append(ShowItem(**show_dict))
        
        return {"results": results}
    except HTTPException:
        # Re-raise HTTPExceptions (validation errors)
        raise
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/download")
async def start_download(download_request: DownloadRequest, background_tasks: BackgroundTasks) -> dict[str, object]:
    """
    Start downloading shows based on filters
    """
    try:
        # Validate target directory
        target_path = Path(download_request.target_directory)
        target_path.mkdir(parents=True, exist_ok=True)

        # Get filtered shows using a fresh database connection
        db_conn = get_db_connection()
        shows = list(db_conn.filtered(download_request.filters))

        if not shows:
            raise HTTPException(status_code=404, detail="No shows found matching filters")

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


async def download_show_background(show_data: dict[str, Any], download_request: DownloadRequest) -> None:
    """
    Background task to handle the actual download
    """
    show_id = str(show_data.get("hash", "unknown"))

    try:
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
        quality = quality_map.get(download_request.quality, ("url_http", "url_http_small", "url_http_hd"))

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
        logger.error(f"Background download failed for {show_id}: {e}")
        if show_id in active_downloads:
            active_downloads[show_id]["status"] = "failed"
            active_downloads[show_id]["message"] = f"Download failed: {str(e)}"


@app.get("/api/download/status/{download_id}")
async def get_download_status(download_id: str) -> dict[str, Any]:
    """
    Get the status of a specific download
    """
    if download_id not in active_downloads:
        raise HTTPException(status_code=404, detail="Download not found")

    return active_downloads[download_id]


@app.get("/api/download/status")
async def get_all_download_statuses() -> dict[str, dict[str, Any]]:
    """
    Get statuses of all active downloads
    """
    return active_downloads


if __name__ == "__main__":
    import uvicorn

    # For development purposes
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
