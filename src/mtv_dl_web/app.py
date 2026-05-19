from pathlib import Path

from flask import Flask, jsonify

from . import config
from .wrapper import Wrapper


def create_app():
    Path(config.mtv_dl_database_dir).mkdir(parents=True, exist_ok=True)

    app = Flask(__name__)

    @app.route("/")
    def hello_world():
        return "Hello, World!"

    @app.route("/list")
    def list_items():
        wrapper = Wrapper(config.mtv_dl_database_dir)
        result = wrapper.list()
        response = jsonify(result)
        response.headers["Content-Type"] = "application/json"
        return response

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host=config.host, port=config.port)
