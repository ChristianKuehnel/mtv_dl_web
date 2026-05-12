#!/usr/bin/env python3
"""
Test for FastAPI backend initialization (Story 1.1)
"""

import sys
from pathlib import Path

# Add the src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_fastapi_app_initialization():
    """Test that FastAPI app initializes correctly"""
    from mtv_dl_web.main import app

    assert hasattr(app, "title"), "FastAPI app should have a title"
    assert hasattr(app, "version"), "FastAPI app should have a version"
    assert app.title == "MTV Downloader Web Interface"
    assert app.version == "1.0.0"


def test_fastapi_routes():
    """Test that basic FastAPI routes are configured"""
    from mtv_dl_web.main import app

    routes = [route.path for route in app.routes]

    assert "/" in routes, "Root route should exist"
    assert "/health" in routes, "Health route should exist"
    assert "/api/search" in routes, "Search API route should exist"
    assert "/api/download" in routes, "Download API route should exist"


def test_project_structure():
    """Test that project structure matches requirements"""
    project_root = Path(__file__).parent.parent

    required_dirs = [
        "src/mtv_dl_web",
        "src/mtv_dl_web/frontend",
        "src/mtv_dl",
    ]

    for dir_path in required_dirs:
        full_path = project_root / dir_path
        assert full_path.exists(), f"Required directory {dir_path} does not exist"
        assert full_path.is_dir(), f"{dir_path} should be a directory"

    required_files = [
        "src/mtv_dl_web/main.py",
        "src/mtv_dl_web/__init__.py",
        "src/__init__.py",
        "src/mtv_dl_web/config/settings.py",
        "src/mtv_dl_web/frontend/hello.html",
        "pyproject.toml",
    ]

    for file_path in required_files:
        full_path = project_root / file_path
        assert full_path.exists(), f"Required file {file_path} does not exist"
        assert full_path.is_file(), f"{file_path} should be a file"


def test_dependencies():
    """Test that project dependencies can be imported"""
    import fastapi
    import pydantic
    import uvicorn

    assert fastapi is not None
    assert pydantic is not None
    assert uvicorn is not None
