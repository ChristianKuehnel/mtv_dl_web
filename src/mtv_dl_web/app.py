from pathlib import Path
import logging

from flask import Flask, jsonify, request

from . import config
from .wrapper import Wrapper


logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def create_app():
    setup_logging()
    Path(config.mtv_dl_database_dir).mkdir(parents=True, exist_ok=True)
    logger.info("Starting MTV Downloader Web Application")
    logger.info("Using mtv_dl database directory: %s", config.mtv_dl_database_dir)

    app = Flask(__name__)
    app.wrapper = Wrapper(config.mtv_dl_database_dir)

    @app.route("/")
    def hello_world():
        logger.debug("Handling request for /")
        return "Hello, World!"

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.route("/list")
    def list_items():
        logger.info(
            "Handling request for /list from %s",
            request.headers.get("X-Forwarded-For", request.remote_addr),
        )
        result = app.wrapper.list()
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
