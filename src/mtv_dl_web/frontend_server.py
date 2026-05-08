#!/usr/bin/env python3
"""
Simple static file server for serving the MTV Downloader frontend
"""

import os
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import webbrowser


class FrontendHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve from frontend directory
        self.directory = str(Path(__file__).parent / "frontend")
        super().__init__(*args, **kwargs)


def run_frontend_server(port=8080):
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
