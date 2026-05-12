#!/usr/bin/env python3
"""
Test for enhanced health endpoint (Story 1.2)
"""

import sys
import time
from datetime import timedelta
from pathlib import Path

from fastapi.testclient import TestClient

# Add the src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "mtv_dl" / "src"))

# Mock the version function to avoid import issues
import importlib.metadata

original_version = importlib.metadata.version


def mock_version(name: str) -> str:
    if name == "mtv_dl":
        return "0.28.0"
    return original_version(name)


importlib.metadata.version = mock_version

import mtv_dl_web.main as main
from mtv_dl_web.main import app

# Restore original version function
importlib.metadata.version = original_version


class FakeCursor:
    def execute(self, query: str) -> None:
        assert query == "SELECT 1"

    def fetchone(self) -> tuple[int]:
        return (1,)


class FakeConnection:
    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        pass

    def cursor(self) -> FakeCursor:
        return FakeCursor()


class FakeDatabase:
    connection = FakeConnection()
    
    # Add attributes needed for health endpoint
    filmliste_version = 1234567890  # Mock timestamp
    filmliste_refresh_after = timedelta(hours=24)  # Mock refresh interval


def test_health_endpoint_functionality(monkeypatch):
    """Test that health endpoint returns proper response"""
    # Mock get_db_connection to support check_for_refresh parameter
    def mock_get_db_connection(check_for_refresh=True):
        return FakeDatabase()
    monkeypatch.setattr(main, "get_db_connection", mock_get_db_connection)
    client = TestClient(app)

    start_time = time.time()
    response = client.get("/health")
    response_time = (time.time() - start_time) * 1000

    assert response.status_code == 200
    assert response_time <= 500
    
    response_data = response.json()
    assert response_data == {"status": "healthy"}
