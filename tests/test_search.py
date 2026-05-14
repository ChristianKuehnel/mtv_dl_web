#!/usr/bin/env python3
"""
Comprehensive test suite for the search API endpoint
Tests all search functionality including success cases, error handling, and edge cases
"""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

import mtv_dl_web.main as main
from mtv_dl_web.main import app

# Create test client
client = TestClient(app)


class FakeDb:
    def __init__(self):
        self.filtered = MagicMock(return_value=[])


@pytest.fixture
def fake_db(monkeypatch):
    db = FakeDb()
    monkeypatch.setattr(main, "get_db_connection", lambda *args, **kwargs: db)
    return db


class FakeDatabaseIntegration:
    def __init__(self, _database_file, _history_file):
        self.connection = object()

    def filtered(self, _filters):
        return [
            {
                "hash": "integration1",
                "channel": "ARD",
                "title": "Integration Show",
                "topic": "News",
                "size": 111,
                "start": "2023-01-03T12:00:00",
                "duration": "30m",
                "age": "1d",
                "region": "DE",
                "downloaded": None,
            }
        ]


def test_search_endpoint_success(fake_db):
    """Test successful search with valid filters"""
    # Mock the database filtered method
    mock_shows = [
        {
            "hash": "test1",
            "channel": "ARD",
            "title": "Test Show 1",
            "topic": "News",
            "size": 100,
            "start": "2023-01-01T12:00:00",
            "duration": "30m",
            "age": "7d",
            "region": "DE",
            "downloaded": None
        },
        {
            "hash": "test2", 
            "channel": "ZDF",
            "title": "Test Show 2",
            "topic": "Documentary",
            "size": 200,
            "start": "2023-01-02T12:00:00",
            "duration": "60m",
            "age": "14d",
            "region": "DE",
            "downloaded": None
        }
    ]
    
    fake_db.filtered.return_value = mock_shows
    response = client.post("/api/search", json={"filters": ["channel=ARD"]})

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 2
    assert data["results"][0]["channel"] == "ARD"
    assert data["results"][1]["channel"] == "ZDF"


def test_search_endpoint_empty_results(fake_db):
    """Test behavior when no shows match filters"""
    fake_db.filtered.return_value = []
    response = client.post("/api/search", json={"filters": ["channel=NonExistent"]})

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 0


def test_search_endpoint_invalid_filters(fake_db):
    """Test error handling for invalid filters"""
    fake_db.filtered.side_effect = Exception("Invalid filter field")
    response = client.post("/api/search", json={"filters": ["invalid_field=value"]})

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Unsupported field" in data["detail"]


def test_search_endpoint_missing_filters():
    """Test error handling when filters are missing"""
    response = client.post("/api/search", json={})
    
    assert response.status_code == 422  # FastAPI validation error
    data = response.json()
    assert "detail" in data


def test_search_endpoint_empty_filters_rejected():
    """Test empty filter list is rejected"""
    response = client.post("/api/search", json={"filters": []})

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "At least one filter is required in filters[]" == data["detail"]


def test_search_endpoint_blank_filter_entry_rejected():
    """Test blank filter entries are rejected."""
    response = client.post("/api/search", json={"filters": ["   "]})

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Filter entries must not be empty"


def test_search_endpoint_filter_allows_operator_whitespace(fake_db):
    """Test filter parsing tolerates whitespace around operator."""
    fake_db.filtered.return_value = []
    response = client.post("/api/search", json={"filters": ["channel   =   ARD"]})

    assert response.status_code == 200
    fake_db.filtered.assert_called_once_with(["channel   =   ARD"])


def test_search_endpoint_malformed_filter_rejected():
    """Test malformed filter string gets format validation error"""
    response = client.post("/api/search", json={"filters": ["channel"]})

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid filter format" in data["detail"]


def test_search_endpoint_database_error(fake_db):
    """Test error handling for database errors"""
    fake_db.filtered.side_effect = Exception("Database connection failed")
    response = client.post("/api/search", json={"filters": ["channel=ARD"]})

    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "Search operation failed" in data["detail"]


def test_search_endpoint_integration_path(monkeypatch):
    """Test route using get_db_connection path without monkeypatching it."""
    monkeypatch.setattr(main, "Database", FakeDatabaseIntegration)
    response = client.post("/api/search", json={"filters": ["channel=ARD"]})

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["hash"] == "integration1"


def test_search_endpoint_complex_filters(fake_db):
    """Test search with multiple complex filters"""
    mock_shows = [
        {
            "hash": "test1",
            "channel": "ARD", 
            "title": "Extra 3",
            "topic": "extra 3",
            "size": 150,
            "start": "2023-01-01T12:00:00",
            "duration": "30m",
            "age": "7d",
            "region": "DE",
            "downloaded": None
        }
    ]
    
    fake_db.filtered.return_value = mock_shows
    # Test with multiple filters
    response = client.post("/api/search", json={
        "filters": ["channel=ARD", "topic='extra 3'", "duration+20m"]
    })

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["title"] == "Extra 3"


def test_search_endpoint_special_characters(fake_db):
    """Test filters with special characters and spaces"""
    mock_shows = [
        {
            "hash": "test1",
            "channel": "ARD",
            "title": "Show with 'quotes' and spaces",
            "topic": "News",
            "size": 100,
            "start": "2023-01-01T12:00:00",
            "duration": "30m",
            "age": "7d",
            "region": "DE",
            "downloaded": None
        }
    ]
    
    fake_db.filtered.return_value = mock_shows
    response = client.post("/api/search", json={
        "filters": ["title='Show with \\'quotes\\' and spaces'"]
    })

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1


def test_search_response_structure(fake_db):
    """Test that response has correct structure"""
    mock_shows = [
        {
            "hash": "test1",
            "channel": "ARD",
            "title": "Test Show",
            "topic": "News", 
            "url_http": "https://example.org/show/test1",
            "size": 100,
            "start": "2023-01-01T12:00:00",
            "duration": "30m",
            "age": "7d",
            "region": "DE",
            "season": 1,
            "episode": 5,
            "downloaded": None
        }
    ]
    
    fake_db.filtered.return_value = mock_shows
    response = client.post("/api/search", json={"filters": ["channel=ARD"]})
    data = response.json()

    # Check response structure
    assert "results" in data
    result = data["results"][0]

    # Verify all expected fields are present
    required_fields = ["hash", "channel", "title", "topic", "url", "size", "start", "duration", "age", "region", "season", "episode"]
    for field in required_fields:
        assert field in result, f"Missing required field: {field}"

    assert result["url"] == "https://example.org/show/test1"
    assert result["season"] == "1"
    assert result["episode"] == "5"


if __name__ == "__main__":
    print("Running comprehensive search API tests...")
    
    # Run all tests
    test_functions = [
        test_search_endpoint_success,
        test_search_endpoint_empty_results,
        test_search_endpoint_invalid_filters,
        test_search_endpoint_missing_filters,
        test_search_endpoint_database_error,
        test_search_endpoint_complex_filters,
        test_search_endpoint_special_characters,
        test_search_response_structure
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__}: {str(e)}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All search API tests passed!")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the implementation.")
        sys.exit(1)
