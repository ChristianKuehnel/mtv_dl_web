"""MTV Downloader Web Application"""

__all__ = ["create_app"]


def __getattr__(name):
    if name == "create_app":
        from .app import create_app

        return create_app

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
