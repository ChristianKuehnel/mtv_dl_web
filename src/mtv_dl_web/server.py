"""Production WSGI server entrypoint."""

from waitress import serve

from . import config
from .app import create_app


def main() -> None:
    """Run the application with a production WSGI server."""
    serve(create_app(), host=config.host, port=config.port)


if __name__ == "__main__":
    main()
