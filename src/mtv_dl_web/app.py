from pathlib import Path
import logging

from flask import Flask, jsonify, request, send_from_directory

from . import config
from .wrapper import Wrapper


logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Configure application logging."""
    logging_level = getattr(logging, config.logging_level.upper(), None)
    if not isinstance(logging_level, int):
        raise ValueError(f"Invalid logging level: {config.logging_level!r}")

    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def create_app():
    setup_logging()
    Path(config.mtv_dl_database_dir).mkdir(parents=True, exist_ok=True)
    Path(config.base_dir).mkdir(parents=True, exist_ok=True)
    logger.info("Starting MTV Downloader Web Application")
    logger.info("Using mtv_dl database directory: %s", config.mtv_dl_database_dir)
    logger.info("Using download base directory: %s", config.base_dir)
    logger.info("Using mtv_dl download path: %s", config.download_path)

    app = Flask(__name__)
    app.wrapper = Wrapper(config.mtv_dl_database_dir, config.download_path)

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
        success = app.wrapper.refresh_database()
        status_code = 200 if success else 500
        response = jsonify({"success": success})
        response.headers["Content-Type"] = "application/json"
        return response, status_code

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

        success = app.wrapper.download(show_hash)
        status_code = 200 if success else 500
        response = jsonify({"success": success})
        response.headers["Content-Type"] = "application/json"
        return response, status_code

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host=config.host, port=config.port)
