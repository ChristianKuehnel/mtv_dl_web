#!/usr/bin/env python3
"""
Simple static file server for serving the MTV Downloader frontend
"""

import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any
import webbrowser


class FrontendHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Serve from frontend directory
        self.directory = str(Path(__file__).parent / "frontend")
        super().__init__(*args, **kwargs)


def run_frontend_server(port: int = 8080) -> None:
    """Run a simple HTTP server for the frontend"""
    handler = FrontendHandler
    server = HTTPServer(("localhost", port), handler)

    print(f"Frontend server starting on http://localhost:{port}")
    print(f"Serving from: {Path(__file__).parent / 'frontend'}")

    try:
        webbrowser.open(f"http://localhost:{port}")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down frontend server...")
        server.shutdown()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_frontend_server(port)
