#!/usr/bin/env python3
"""
Unit tests for MTV Downloader Web Interface
"""

import sys
import os
from unittest.mock import patch, MagicMock

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app
from fastapi.testclient import TestClient


def test_health_endpoint():
    """Test that health endpoint returns 200"""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_homepage_serves_hello_world():
    """Test that homepage serves hello world page"""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "Hello World" in response.text
    assert "Welcome to the MTV Downloader Web Interface" in response.text


def test_api_search_endpoint_not_implemented():
    """Test that search endpoint exists but raises 404 (no data)"""
    client = TestClient(app)
    response = client.post("/api/search", json={"filters": []})
    assert response.status_code == 404  # No database to search in


def test_api_download_endpoint_not_implemented():
    """Test that download endpoint exists but raises 404 (no data)"""
    client = TestClient(app)
    response = client.post("/api/download", json={})
    assert response.status_code == 404  # No database to download from


if __name__ == "__main__":
    # Run tests manually for development
    test_health_endpoint()
    test_homepage_serves_hello_world()
    test_api_search_endpoint_not_implemented()
    test_api_download_endpoint_not_implemented()
    print("All tests passed!")