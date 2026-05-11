#!/usr/bin/env python3
"""
Test for enhanced health endpoint (Story 1.2)
"""

import sys
import time
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


def test_health_endpoint_functionality(monkeypatch):
    """Test that health endpoint returns proper response"""
    monkeypatch.setattr(main, "check_database_connectivity", lambda: None)
    client = TestClient(app)

    start_time = time.time()
    response = client.get("/health")
    response_time = (time.time() - start_time) * 1000

    assert response.status_code == 200
    assert response_time <= 500
    assert response.json() == {"status": "healthy"}
