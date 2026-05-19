from flask import Flask, jsonify
from .wrapper import Wrapper


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def hello_world():
        return "Hello, World!"

    @app.route("/list")
    def list_items():
        wrapper = Wrapper()
        result = wrapper.list()
        response = jsonify(result)
        response.headers["Content-Type"] = "application/json"
        return response

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
