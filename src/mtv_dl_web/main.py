#!/usr/bin/env python3
"""
Web Interface for MTV Downloader
A lightweight web interface for the MediathekView Downloader with Python backend
supporting concurrent web requests and downloads.
"""

import logging
import os
import re
import threading
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock
from time import perf_counter
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Import the mtv_dl functionality
try:
    from mtv_dl.mtv_dl import Database, Downloader
except ImportError as e:
    print(f"Failed to import mtv_dl: {e}")
    raise

# Import settings
from mtv_dl_web.config.settings import settings

# Configure logging
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize and cleanup background scheduler for app lifecycle."""
    initialize_database_refresh_scheduler()
    try:
        yield
    finally:
        global database_refresh_scheduler

        if database_refresh_scheduler is not None:
            database_refresh_scheduler.shutdown(wait=False)
            database_refresh_scheduler = None


# Initialize FastAPI app
app = FastAPI(
    title="MTV Downloader Web Interface",
    description="A lightweight web interface for downloading videos from German public broadcasting services",
    version="1.0.0",
    lifespan=lifespan,
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
active_downloads_lock = threading.RLock()
database_update_lock = Lock()
_database_update_count = 0

# Database refresh management
database_refresh_lock = threading.Lock()
is_database_refreshing = False
database_last_refresh_time = 0.0
database_last_refresh_duration_seconds: float | None = None
database_last_refresh_source = "none"
database_refresh_task: threading.Thread | None = None
database_refresh_scheduler: BackgroundScheduler | None = None
database_refresh_schedule_config: str = "0 0 * * *"  # Default 24h cadence (midnight)


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


class SearchResponse(BaseModel):
    results: list[ShowItem]


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

FILTER_PATTERN = re.compile(r"^(?P<field>\w+)\s*(?P<operator>!=|=|\+|-)\s*(?P<pattern>.+)$")


def validate_cron_expression(cron_expr: str) -> bool:
    """
    Validate a cron expression using APScheduler's CronTrigger

    Args:
        cron_expr: Cron expression to validate

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        from apscheduler.triggers.cron import CronTrigger

        CronTrigger.from_crontab(cron_expr)
        return True
    except Exception:
        return False


def initialize_database_refresh_scheduler() -> None:
    """Initialize the database refresh scheduler with configured schedule."""
    global database_refresh_schedule_config, database_refresh_scheduler

    # Read configuration for refresh schedule
    refresh_schedule = getattr(settings, "database_refresh_schedule", None)

    if refresh_schedule:
        # Validate the cron expression
        if not validate_cron_expression(refresh_schedule):
            logger.error(f"Invalid database refresh schedule configuration: {refresh_schedule}")
            raise ValueError(f"Invalid cron expression: {refresh_schedule}")
        database_refresh_schedule_config = refresh_schedule
        logger.info(f"Using configured database refresh schedule: {refresh_schedule}")
    else:
        database_refresh_schedule_config = "0 0 * * *"  # Default 24h cadence (midnight)
        logger.info("Using default database refresh schedule: 0 0 * * * (daily at midnight)")

    # Create background scheduler
    database_refresh_scheduler = BackgroundScheduler()

    # Schedule the refresh job
    database_refresh_scheduler.add_job(
        refresh_database_background,
        "cron",
        minute=database_refresh_schedule_config.split()[0],
        hour=database_refresh_schedule_config.split()[1],
        day=database_refresh_schedule_config.split()[2],
        month=database_refresh_schedule_config.split()[3],
        day_of_week=database_refresh_schedule_config.split()[4],
        kwargs={"trigger_source": "scheduled"},
        name="database_refresh_job",
        misfire_grace_time=300,  # 5 minute grace period
        coalesce=True,
        max_instances=1,
    )

    # Start the scheduler
    database_refresh_scheduler.start()
    logger.info("Database refresh scheduler started")


def validate_filters(filters: list[str]) -> None:
    """
    Validate that filters use supported operators and fields

    Args:
        filters: List of filter strings to validate

    Raises:
        HTTPException: 400 Bad Request if invalid operators or fields are found
    """
    if not filters:
        logger.error("Filter validation failed: empty filter list")
        raise HTTPException(status_code=400, detail="At least one filter is required in filters[]")

    for filter_str in filters:
        normalized_filter = filter_str.strip()
        if not normalized_filter:
            logger.error("Filter validation failed: blank filter")
            raise HTTPException(status_code=400, detail="Filter entries must not be empty")

        # Parse filter string using the same regex as mtv_dl
        match = FILTER_PATTERN.match(normalized_filter)
        if not match:
            logger.error(f"Filter validation failed: invalid format '{filter_str}'")
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
            logger.error(f"Filter validation failed: unsupported operator '{operator}' in '{filter_str}'")
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported operator '{operator}' in filter: '{filter_str}'. "
                f"Supported operators: {', '.join(sorted(SUPPORTED_OPERATORS))}",
            )

        # Validate field
        if field not in SUPPORTED_FIELDS:
            logger.error(f"Filter validation failed: unsupported field '{field}' in '{filter_str}'")
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported field '{field}' in filter: '{filter_str}'. "
                f"Supported fields: {', '.join(sorted(SUPPORTED_FIELDS))}",
            )


# Database configuration
configured_database_path = Path(settings.database_path).expanduser()
DATABASE_DIR = configured_database_path.parent if configured_database_path.suffix else configured_database_path
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_FILE = configured_database_path if configured_database_path.suffix else DATABASE_DIR / "filmliste.sqlite"
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


def get_db_connection(
    check_for_refresh: bool = True, background_tasks: BackgroundTasks | None = None, is_refresh_operation: bool = False
) -> Database:
    """
    Create a new database connection for each request to avoid thread-safety issues

    Args:
        check_for_refresh: Whether to check if database needs refresh (default True)
        background_tasks: Background tasks to add refresh job to if needed
        is_refresh_operation: Whether this is a refresh operation (should not trigger refreshes)

    Returns:
        Database: A new database connection instance
    """
    try:
        db = Database(DATABASE_FILE, HISTORY_FILE)
        # Only check for refresh if this is not a refresh operation
        if os.environ.get("MTV_DL_WEB_SKIP_DB_UPDATE") != "1" and check_for_refresh and not is_refresh_operation:
            # This is a standard request, so we don't want to trigger refresh from here
            # The scheduler will handle refreshes
            pass  # Skip refresh trigger during regular request handling
        logger.debug("Database connection created successfully")
        return db
    except Exception as e:
        logger.error(f"Failed to create database connection: {e}")
        raise


def _schedule_refresh_job(background_tasks: BackgroundTasks | None, trigger_source: str) -> bool:
    """Schedule a database refresh job without blocking request handling."""
    global database_refresh_task, is_database_refreshing

    with database_refresh_lock:
        if is_database_refreshing:
            return False
        is_database_refreshing = True

    if background_tasks is not None:
        background_tasks.add_task(refresh_database_background, trigger_source)
        database_refresh_task = None
        return True

    try:
        refresh_thread = threading.Thread(
            target=refresh_database_background, kwargs={"trigger_source": trigger_source}, daemon=True
        )
        refresh_thread.start()
        database_refresh_task = refresh_thread
        return True
    except Exception as e:
        with database_refresh_lock:
            is_database_refreshing = False
        logger.error(f"Failed to schedule database refresh job: {e}")
        return False


def check_and_refresh_database_if_needed(db: Database, background_tasks: BackgroundTasks | None = None) -> None:
    """
    Check if database needs refresh and trigger it in background if needed.
    This function should not be called from search/download request paths.
    Instead, search/download requests should only check database connectivity.

    Args:
        db: Database instance to check
    """
    global is_database_refreshing, database_last_refresh_time, database_refresh_task

    # Get current timestamp for tracking
    current_time = datetime.now().timestamp()

    # For search/download requests, we shouldn't trigger refreshes - just check connectivity
    # This is handled by the caller, not this function
    logger.debug("Database refresh check bypassed for request-based access")


def refresh_database_background(trigger_source: str = "scheduled") -> None:
    """
    Background task to refresh the database without blocking web requests

    This function implements logging for refresh start/success/failure/duration/source
    """
    global database_last_refresh_duration_seconds, database_last_refresh_source
    global database_last_refresh_time, is_database_refreshing, database_refresh_task

    start_time = perf_counter()
    logger.info(f"Starting database refresh (source={trigger_source})")

    try:
        # Perform the actual database refresh
        # Note: We create a new database instance for the refresh to avoid
        # conflicts with the main connection
        set_database_update_in_progress(True)
        try:
            refresh_db = Database(DATABASE_FILE, HISTORY_FILE)
            refresh_db.update_if_old()
        finally:
            set_database_update_in_progress(False)

        duration = perf_counter() - start_time
        with database_refresh_lock:
            database_last_refresh_time = datetime.now().timestamp()
            database_last_refresh_duration_seconds = duration
            database_last_refresh_source = trigger_source
        logger.info(
            f"Database refresh completed (source={trigger_source}, outcome=success, duration_seconds={duration:.2f})"
        )

    except Exception as e:
        duration = perf_counter() - start_time
        with database_refresh_lock:
            database_last_refresh_duration_seconds = duration
            database_last_refresh_source = trigger_source
        logger.error(
            f"Database refresh failed (source={trigger_source}, outcome=failure, duration_seconds={duration:.2f}): {e}"
        )
    finally:
        with database_refresh_lock:
            is_database_refreshing = False
            database_refresh_task = None
            logger.info(f"Database refresh task completed (source={trigger_source})")


def get_database_refresh_status() -> dict[str, Any]:
    """
    Get current database refresh status including metadata for UI/API

    Returns:
        Dictionary containing refresh status information including timestamps
    """
    with database_refresh_lock:
        return {
            "is_refreshing": is_database_refreshing,
            "last_refresh_time": database_last_refresh_time,
            "status": "refreshing" if is_database_refreshing else "idle",
            "last_refresh_duration": database_last_refresh_duration_seconds,
            "last_refresh_source": database_last_refresh_source,
        }


def get_database_metadata() -> dict[str, Any]:
    """
    Get metadata about the database including age and refresh information

    Returns:
        Dictionary containing database metadata
    """
    try:
        db = Database(DATABASE_FILE, HISTORY_FILE)
        # Try to get database age information
        current_time = datetime.now().timestamp()
        database_age = None
        last_refresh_timestamp = database_last_refresh_time

        # Check if we can get meaningful age info from the database
        if hasattr(db, "filmliste_version"):
            database_age = current_time - db.filmliste_version
        elif database_last_refresh_time > 0:
            # Fallback to last refresh time if no version info
            database_age = current_time - database_last_refresh_time

        return {
            "last_refresh_time": last_refresh_timestamp,
            "database_age_seconds": database_age,
            "database_age_readable": str(timedelta(seconds=database_age)) if database_age is not None else None,
        }
    except Exception as e:
        logger.warning(f"Could not retrieve database metadata: {e}")
        return {
            "last_refresh_time": database_last_refresh_time,
            "database_age_seconds": None,
            "database_age_readable": None,
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
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint that verifies service readiness

    Returns:
        JSON: { "status": "healthy" } or { "status": "unhealthy" } with database info
    """
    start_time = perf_counter()
    refresh_status = get_database_refresh_status()
    is_updating = is_database_update_in_progress() or refresh_status["is_refreshing"]
    status = "updating" if is_updating else "healthy"

    try:
        check_database_connectivity()
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        status = "unhealthy"

    response_time_ms = round((perf_counter() - start_time) * 1000, 2)
    logger.info(f"Health check: {status}, response time: {response_time_ms}ms")

    if response_time_ms > 1000:
        logger.warning(f"Health check response time {response_time_ms}ms exceeds 1000ms threshold")
        status = "unhealthy"

    return {
        "status": status,
        "database": {
            "is_refreshing": refresh_status["is_refreshing"],
            "last_refresh_time": refresh_status["last_refresh_time"],
            "refresh_status": refresh_status["status"],
        },
    }


@app.post("/api/search", response_model=SearchResponse)
async def search_shows(filters: SearchFilters, background_tasks: BackgroundTasks) -> SearchResponse:
    """
    Search for shows based on filters

    Validates filter operators and fields before processing the search.
    """
    try:
        # Validate filters before processing
        validate_filters(filters.filters)

        # Perform the search using a fresh database connection
        # This will not trigger background refresh (as designed)
        db_conn = get_db_connection(check_for_refresh=False, is_refresh_operation=False)
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

        return SearchResponse(results=results)
    except HTTPException:
        # Re-raise HTTPExceptions (validation errors)
        raise
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Search operation failed")


@app.post("/api/download")
async def start_download(download_request: DownloadRequest, background_tasks: BackgroundTasks) -> dict[str, object]:
    """
    Start downloading shows based on filters
    """
    try:
        # Validate target directory
        target_path = Path(download_request.target_directory).expanduser()
        target_path.mkdir(parents=True, exist_ok=True)

        # Get filtered shows using a fresh database connection
        # This will not trigger background refresh (as designed)
        db_conn = get_db_connection(check_for_refresh=False, is_refresh_operation=False)
        shows = list(db_conn.filtered(download_request.filters))

        if not shows:
            raise HTTPException(status_code=404, detail="No shows found matching filters")

        # Process each show in the background
        download_ids = []
        for show in shows:
            show_id = show["hash"]
            download_ids.append(show_id)

            # Add to active downloads
            with active_downloads_lock:
                active_downloads[show_id] = {
                    "status": "queued",
                    "progress": 0.0,
                    "message": "Queued for download",
                    "file_path": None,
                }

            # Submit download task to background
            background_tasks.add_task(download_show_background, show, download_request, target_path)

        return {
            "message": f"Started downloading {len(shows)} shows",
            "download_ids": download_ids,
        }

    except Exception as e:
        logger.error(f"Download start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def download_show_background(
    show_data: dict[str, Any], download_request: DownloadRequest, target_path: Path
) -> None:
    """
    Background task to handle the actual download
    """
    show_id = str(show_data.get("hash", "unknown"))

    try:
        # Update status
        with active_downloads_lock:
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
            target=target_path,
            include_subtitles=download_request.include_subtitles,
            include_nfo=download_request.include_nfo,
            merge_to_mkv=download_request.merge_to_mkv,
        )

        # Update status
        with active_downloads_lock:
            if path:
                active_downloads[show_id]["status"] = "completed"
                active_downloads[show_id]["message"] = "Download completed"
                active_downloads[show_id]["file_path"] = str(path)
            else:
                active_downloads[show_id]["status"] = "failed"
                active_downloads[show_id]["message"] = "Download failed"

    except Exception as e:
        logger.error(f"Background download failed for {show_id}: {e}")
        with active_downloads_lock:
            if show_id in active_downloads:
                active_downloads[show_id]["status"] = "failed"
                active_downloads[show_id]["message"] = f"Download failed: {str(e)}"


@app.get("/api/download/status/{download_id}")
async def get_download_status(download_id: str) -> dict[str, Any]:
    """
    Get the status of a specific download
    """
    with active_downloads_lock:
        if download_id not in active_downloads:
            raise HTTPException(status_code=404, detail="Download not found")

        return active_downloads[download_id]


@app.get("/api/download/status")
async def get_all_download_statuses() -> dict[str, dict[str, Any]]:
    """
    Get statuses of all active downloads
    """
    with active_downloads_lock:
        return active_downloads


@app.delete("/api/download/status/{download_id}")
async def remove_download_status(download_id: str) -> dict[str, str]:
    """Remove a download entry from the in-memory queue/status list."""
    await run_in_threadpool(_remove_download_status_locked, download_id)
    return {"message": "Download removed", "download_id": download_id}


def _remove_download_status_locked(download_id: str) -> None:
    """Remove a download status entry while holding the shared-state lock."""
    with active_downloads_lock:
        if download_id not in active_downloads:
            raise HTTPException(status_code=404, detail="Download not found")
        del active_downloads[download_id]


@app.get("/api/database/status")
async def get_database_status() -> dict[str, Any]:
    """
    Get current database status including refresh information

    Returns:
        JSON: { "is_refreshing": bool, "status": str, "last_refresh_time": float }
    """
    db_status = get_database_refresh_status()

    # Get additional metadata
    metadata = await run_in_threadpool(get_database_metadata)

    # Combine status and metadata
    result = {
        "is_refreshing": db_status["is_refreshing"],
        "status": db_status["status"],
        "last_refresh_time": db_status["last_refresh_time"],
        "last_refresh_duration": db_status["last_refresh_duration"],
        "last_refresh_source": db_status["last_refresh_source"],
        "database_age_seconds": metadata["database_age_seconds"],
        "database_age_readable": metadata["database_age_readable"],
    }

    return result


@app.post("/api/database/refresh")
async def trigger_manual_refresh(background_tasks: BackgroundTasks) -> dict[str, str]:
    """
    Manually trigger a database refresh (for testing/debugging purposes)

    Returns:
        JSON: Success confirmation
    """
    if _schedule_refresh_job(background_tasks, "manual"):
        return {"message": "Manual refresh started"}
    if is_database_refreshing:
        return {"message": "Refresh already in progress"}
    return {"message": "Failed to start manual refresh"}


if __name__ == "__main__":
    import uvicorn

    # For development purposes
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
