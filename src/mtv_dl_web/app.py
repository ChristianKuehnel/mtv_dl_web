from pathlib import Path
import logging
from typing import Protocol

from flask import Flask, jsonify, request, send_from_directory

from . import config
from .queue import DownloadQueue
from .scheduler import DatabaseRefreshScheduler
from .wrapper import Wrapper


logger = logging.getLogger(__name__)


class DatabaseWrapper(Protocol):
    def database_age(self) -> object: ...

    def refresh_database(self) -> bool: ...


def setup_logging() -> None:
    """Configure application logging."""
    logging_level = getattr(logging, config.logging_level.upper(), None)
    if not isinstance(logging_level, int):
        raise ValueError(f"Invalid logging level: {config.logging_level!r}")

    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def ensure_database_available(wrapper: DatabaseWrapper) -> None:
    """Initialize the mtv_dl database when the health probe cannot read it."""
    try:
        wrapper.database_age()
        return
    except RuntimeError as e:
        logger.warning("mtv_dl database age probe failed during startup: %s", e)

    logger.info("Refreshing mtv_dl database during startup")
    if not wrapper.refresh_database():
        raise RuntimeError("mtv_dl database startup refresh failed")


def create_app():
    setup_logging()
    try:
        Path(config.mtv_dl_database_dir).mkdir(parents=True, exist_ok=True)
        Path(config.base_dir).mkdir(parents=True, exist_ok=True)
        config.validate_runtime_permissions()
    except OSError as e:
        logger.critical("Startup permission check failed: %s", e)
        raise SystemExit(1) from e

    logger.info("Starting MTV Downloader Web Application")
    logger.info("Using mtv_dl database directory: %s", config.mtv_dl_database_dir)
    logger.info("Using download base directory: %s", config.base_dir)
    logger.info("Using mtv_dl download path: %s", config.download_path)

    app = Flask(__name__)
    app.wrapper = Wrapper(
        config.mtv_dl_database_dir,
        config.download_path,
        config.exclude_audiodeskription,
    )
    try:
        ensure_database_available(app.wrapper)
    except RuntimeError as e:
        logger.critical("Startup database check failed: %s", e)
        raise SystemExit(1) from e

    app.download_queue = DownloadQueue(app.wrapper)
    app.database_refresh_scheduler = None
    if config.database_refresh_enabled:
        app.database_refresh_scheduler = DatabaseRefreshScheduler(
            app.download_queue,
            config.database_refresh_cron,
            config.database_refresh_timezone,
        )
        app.database_refresh_scheduler.start()

    @app.route("/")
    def index():
        logger.debug("Handling request for /")
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/health")
    def health():
        try:
            last_db_update = app.wrapper.database_age()
        except RuntimeError as e:
            response = jsonify({"error": str(e), "status": "error"})
            response.headers["Content-Type"] = "application/json"
            return response, 500

        return jsonify(
            {
                "last_db_update": last_db_update.isoformat(),
                "status": "ok",
            }
        )

    @app.route("/list")
    def list_items():
        logger.info(
            "Handling request for /list from %s",
            request.headers.get("X-Forwarded-For", request.remote_addr),
        )
        if app.download_queue.database_refresh_running():
            response = jsonify(
                {"error": "Database refresh in progress. Please try again later."}
            )
            response.headers["Content-Type"] = "application/json"
            return response, 409

        filter_queries = request.args.getlist("filter")
        try:
            result = app.wrapper.list(filter_queries)
        except ValueError as e:
            response = jsonify({"error": str(e)})
            response.headers["Content-Type"] = "application/json"
            return response, 400
        except RuntimeError as e:
            response = jsonify({"error": str(e)})
            response.headers["Content-Type"] = "application/json"
            return response, 500

        response = jsonify(result)
        response.headers["Content-Type"] = "application/json"
        return response

    @app.route("/refresh_database")
    def refresh_database():
        logger.info(
            "Handling request for /refresh_database from %s",
            request.headers.get("X-Forwarded-For", request.remote_addr),
        )
        job = app.download_queue.enqueue_database_refresh()
        response = jsonify({"job_id": job.id, "status": "queued", "success": True})
        response.headers["Content-Type"] = "application/json"
        return response

    @app.route("/download")
    def download():
        logger.info(
            "Handling request for /download from %s",
            request.headers.get("X-Forwarded-For", request.remote_addr),
        )
        show_hash = request.args.get("hash")
        if not show_hash:
            response = jsonify({"error": "hash is required"})
            response.headers["Content-Type"] = "application/json"
            return response, 400

        title = request.args.get("title") or None
        job = app.download_queue.enqueue(show_hash, title)
        response = jsonify({"job_id": job.id, "status": "queued", "success": True})
        response.headers["Content-Type"] = "application/json"
        return response

    @app.route("/queue")
    def queue():
        logger.info(
            "Handling request for /queue from %s",
            request.headers.get("X-Forwarded-For", request.remote_addr),
        )
        response = jsonify(app.download_queue.snapshot())
        response.headers["Content-Type"] = "application/json"
        return response

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host=config.host, port=config.port)
