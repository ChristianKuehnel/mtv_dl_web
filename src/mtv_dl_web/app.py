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

    @app.route("/")
    def hello_world():
        logger.debug("Handling request for /")
        return "Hello, World!"

    @app.route("/list")
    def list_items():
        logger.info(
            "Handling request for /list from %s",
            request.headers.get("X-Forwarded-For", request.remote_addr),
        )
        wrapper = Wrapper(config.mtv_dl_database_dir)
        result = wrapper.list()
        response = jsonify(result)
        response.headers["Content-Type"] = "application/json"
        return response

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host=config.host, port=config.port)
