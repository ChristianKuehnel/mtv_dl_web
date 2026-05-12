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
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock
from time import perf_counter
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
database_update_lock = Lock()
_database_update_count = 0

# Database refresh management
database_refresh_lock = threading.Lock()
is_database_refreshing = False
database_last_refresh_time = 0.0
database_refresh_task = None  # Track the current refresh task
refresh_cooldown_seconds = 3600  # 1 hour cooldown
refresh_retry_delay = 300  # 5 minute retry delay on failure


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


def set_database_update_in_progress(is_in_progress: bool) -> None:
    """Record whether mtv_dl is refreshing the show database."""
    global _database_update_count

    with database_update_lock:
        if is_in_progress:
            _database_update_count += 1
        else:
            _database_update_count = max(0, _database_update_count - 1)


def is_database_update_in_progress() -> bool:
    """Return true while mtv_dl database refresh work is active."""
    with database_update_lock:
        return _database_update_count > 0


def check_database_connectivity() -> None:
    """Verify that the database can be opened and queried without refreshing it."""
    db_conn = Database(DATABASE_FILE, HISTORY_FILE)
    with db_conn.connection:
        cursor = db_conn.connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()


def get_db_connection(check_for_refresh: bool = True) -> Database:
    """
    Create a new database connection for each request to avoid thread-safety issues

    Args:
        check_for_refresh: Whether to check if database needs refresh (default True)

    Returns:
        Database: A new database connection instance
    """
    try:
        db = Database(DATABASE_FILE, HISTORY_FILE)
        if os.environ.get("MTV_DL_WEB_SKIP_DB_UPDATE") != "1" and check_for_refresh:
            check_and_refresh_database_if_needed(db)
        logger.debug("Database connection created successfully")
        return db
    except Exception as e:
        logger.error(f"Failed to create database connection: {e}")
        raise


def check_and_refresh_database_if_needed(db: Database) -> None:
    """
    Check if database needs refresh and trigger it in background if needed

    Args:
        db: Database instance to check
    """
    global is_database_refreshing, database_last_refresh_time, database_refresh_task

    # Get current timestamp for tracking
    current_time = datetime.now().timestamp()

    # Check if we need to refresh (properly evaluate age)
    try:
        # Check database age properly - compare actual age with refresh threshold
        # If filmliste_version is not available, we can't determine age safely
        needs_refresh = False
        if hasattr(db, "filmliste_version") and hasattr(db, "filmliste_refresh_after"):
            database_age = current_time - db.filmliste_version
            refresh_threshold = db.filmliste_refresh_after.total_seconds()
            needs_refresh = database_age > refresh_threshold
        # If we can't determine age, we'll skip refresh for safety
    except Exception as e:
        # If any error occurs in age checking, assume no refresh is needed
        logger.debug(f"Could not determine if refresh needed: {e}")
        needs_refresh = False

    with database_refresh_lock:
        # If database needs refresh and no refresh is currently in progress
        if needs_refresh and not is_database_refreshing:
            # Check if enough time has passed since last refresh attempt
            if current_time - database_last_refresh_time > refresh_cooldown_seconds:
                # Try to ensure we don't queue multiple refreshes
                if database_refresh_task and not database_refresh_task.done():
                    logger.debug("Database refresh already queued, skipping")
                    return

                is_database_refreshing = True
                database_last_refresh_time = current_time
                logger.info("Database refresh needed, starting background refresh...")
                # Start background refresh
                try:
                    database_refresh_task = asyncio.create_task(refresh_database_background(db))
                except RuntimeError:
                    # No running event loop (e.g., in test environment)
                    logger.debug("No async event loop available, database refresh will be deferred")
                    is_database_refreshing = False  # Reset flag since we can't start refresh
                    # Schedule retry after delay
                    try:
                        retry_task = asyncio.create_task(_retry_database_refresh(db))
                    except RuntimeError:
                        pass  # Can't schedule retry, that's okay
            else:
                logger.debug("Database refresh needed but cooldown period active, skipping for now")
        elif is_database_refreshing:
            logger.debug("Database refresh already in progress, using existing connection")
        else:
            logger.debug("Database is up to date, no refresh needed")


async def _retry_database_refresh(db: Database) -> None:
    """Retry database refresh after a delay if initial attempt failed."""
    await asyncio.sleep(refresh_retry_delay)
    # Attempt to retry refresh after delay
    with database_refresh_lock:
        if not is_database_refreshing:
            # Retry can happen when the cooldown period has passed
            # This is called in case initial attempt failed due to event loop issues
            pass


async def refresh_database_background(db: Database) -> None:
    """
    Background task to refresh the database without blocking web requests

    Args:
        db: Database instance to refresh
    """
    global is_database_refreshing, database_refresh_task

    try:
        logger.info("Starting database refresh in background...")

        # Perform the actual database refresh
        # Note: We create a new database instance for the refresh to avoid
        # conflicts with the main connection
        refresh_db = Database(DATABASE_FILE, HISTORY_FILE)
        refresh_db.update_filmliste()

        logger.info("Database refresh completed successfully")

    except Exception as e:
        logger.error(f"Background database refresh failed: {e}")
        # Even on failure, we still want to mark the refresh as complete
        # to allow future refresh attempts
        logger.info("Database refresh failed but marking as complete to allow retries")
    finally:
        # Ensure we release the lock even if refresh fails
        with database_refresh_lock:
            is_database_refreshing = False
            database_refresh_task = None  # Clear task reference
            logger.info("Database refresh task completed")


def get_database_refresh_status() -> dict[str, Any]:
    """
    Get current database refresh status

    Returns:
        Dictionary containing refresh status information
    """
    with database_refresh_lock:
        return {
            "is_refreshing": is_database_refreshing,
            "last_refresh_time": database_last_refresh_time,
            "status": "refreshing" if is_database_refreshing else "idle",
        }


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
        JSON: { "status": "healthy" } or { "status": "unhealthy" } with database info
    """
    start_time = perf_counter()
    status = "updating" if is_database_update_in_progress() else "healthy"

    try:
        DATABASE_DIR.mkdir(parents=True, exist_ok=True)
        if status == "healthy":
            check_database_connectivity()
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        status = "unhealthy"

    response_time_ms = round((perf_counter() - start_time) * 1000, 2)
    logger.info(f"Health check: {status}, response time: {response_time_ms}ms")

    if response_time_ms > 1000:
        logger.warning(f"Health check response time {response_time_ms}ms exceeds 1000ms threshold")
        status = "unhealthy"

    return {"status": status}


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
        # This will trigger background refresh if needed, but won't block
        db_conn = get_db_connection()
        shows = list(db_conn.filtered(filters.filters))

        # Convert datetime and timedelta objects to strings for Pydantic validation
        results = []
        for show in shows:
            show_dict = dict(show)
            # Convert datetime objects to ISO format strings
            if isinstance(show_dict.get("start"), datetime):
                show_dict["start"] = show_dict["start"].isoformat()
            if isinstance(show_dict.get("downloaded"), datetime):
                show_dict["downloaded"] = show_dict["downloaded"].isoformat()
            # Convert timedelta objects to string representation
            if isinstance(show_dict.get("duration"), timedelta):
                show_dict["duration"] = str(show_dict["duration"])
            if isinstance(show_dict.get("age"), timedelta):
                show_dict["age"] = str(show_dict["age"])
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
        # This will trigger background refresh if needed, but won't block
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


@app.get("/api/database/status")
async def get_database_status() -> dict[str, Any]:
    """
    Get current database status including refresh information

    Returns:
        JSON: { "is_refreshing": bool, "status": str, "last_refresh_time": float }
    """
    db_status = get_database_refresh_status()

    # Return simplified status as originally intended
    return {
        "is_refreshing": db_status["is_refreshing"],
        "status": db_status["status"],
        "last_refresh_time": db_status["last_refresh_time"],
    }


if __name__ == "__main__":
    import uvicorn

    # For development purposes
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
