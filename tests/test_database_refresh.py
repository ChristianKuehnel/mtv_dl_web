#!/usr/bin/env python3
"""
Tests for database refresh scheduler and related functionality
"""

from unittest.mock import patch

from fastapi.testclient import TestClient
import pytest

import mtv_dl_web.main as main
from mtv_dl_web.main import app, validate_cron_expression, get_database_metadata


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
    filmliste_refresh_after = None  # Mock refresh interval


def test_validate_cron_expression_valid():
    """Test that valid cron expressions are accepted"""
    assert validate_cron_expression("0 0 * * *") is True  # Daily at midnight
    assert validate_cron_expression("0 12 * * *") is True  # Daily at noon
    assert validate_cron_expression("0 0 * * 0") is True  # Weekly on Sunday
    assert validate_cron_expression("*/30 * * * *") is True  # Every 30 minutes


def test_validate_cron_expression_invalid():
    """Test that invalid cron expressions are rejected"""
    assert validate_cron_expression("invalid") is False
    assert validate_cron_expression("61 0 * * *") is False  # Invalid minute
    assert validate_cron_expression("0 25 * * *") is False  # Invalid hour
    assert validate_cron_expression("0 0 32 * *") is False  # Invalid day
    assert validate_cron_expression("0 0 * * 8") is False  # Invalid day of week


def test_database_metadata_retrieval():
    """Test database metadata retrieval function"""
    # Mock database to avoid actual DB connections during tests
    fake_db = FakeDatabase()
    
    with patch('mtv_dl_web.main.Database', return_value=fake_db):
        metadata = get_database_metadata()
        assert "last_refresh_time" in metadata
        assert "database_age_seconds" in metadata
        assert "database_age_readable" in metadata


def test_database_status_endpoint():
    """Test database status endpoint returns expected fields"""
    # Mock database and scheduler to avoid actual refresh
    with patch('mtv_dl_web.main.Database', return_value=FakeDatabase()):
        client = TestClient(app)
        
        # Test that status endpoint returns expected structure
        response = client.get("/api/database/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "is_refreshing" in data
        assert "status" in data
        assert "last_refresh_time" in data
        assert "last_refresh_duration" in data
        assert "last_refresh_source" in data
        assert "database_age_seconds" in data
        assert "database_age_readable" in data


def test_manual_refresh_endpoint():
    """Test manual refresh endpoint"""
    with patch('mtv_dl_web.main.Database', return_value=FakeDatabase()), patch(
        'mtv_dl_web.main._schedule_refresh_job', return_value=True
    ):
        client = TestClient(app)

        # Test manual refresh trigger
        response = client.post("/api/database/refresh")
        assert response.status_code == 200
        assert response.json() == {"message": "Manual refresh started"}


def test_manual_refresh_endpoint_already_in_progress():
    """Test manual refresh endpoint while refresh is already running"""
    with patch('mtv_dl_web.main.Database', return_value=FakeDatabase()), patch(
        'mtv_dl_web.main._schedule_refresh_job', return_value=False
    ), patch('mtv_dl_web.main.is_database_refreshing', True):
        client = TestClient(app)

        response = client.post("/api/database/refresh")
        assert response.status_code == 200
        assert response.json() == {"message": "Refresh already in progress"}


def test_manual_refresh_endpoint_failed_to_start():
    """Test manual refresh endpoint when start fails"""
    with patch('mtv_dl_web.main.Database', return_value=FakeDatabase()), patch(
        'mtv_dl_web.main._schedule_refresh_job', return_value=False
    ), patch('mtv_dl_web.main.is_database_refreshing', False):
        client = TestClient(app)

        response = client.post("/api/database/refresh")
        assert response.status_code == 200
        assert response.json() == {"message": "Failed to start manual refresh"}


if __name__ == "__main__":
    # Run tests directly if script is called
    test_validate_cron_expression_valid()
    test_validate_cron_expression_invalid()
    test_database_metadata_retrieval()
    test_database_status_endpoint()
    test_manual_refresh_endpoint()
    print("All tests passed!")
