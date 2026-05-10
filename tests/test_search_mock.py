#!/usr/bin/env python3
"""
Comprehensive test suite for the search API endpoint
Tests all search functionality including success cases, error handling, and edge cases
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock, Mock
from fastapi.testclient import TestClient

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock the mtv_dl module to avoid dependency issues
sys.modules['mtv_dl'] = Mock()
sys.modules['mtv_dl.mtv_dl'] = Mock()
sys.modules['mtv_dl.src'] = Mock()
sys.modules['mtv_dl.src.mtv_dl'] = Mock()

# Create a mock Database class
class MockDatabase:
    def __init__(self, database_file, history_file):
        self.database_file = database_file
        self.history_file = history_file
        
    def update_if_old(self):
        # Mock method - do nothing
        pass
        
    def filtered(self, filters):
        # Return mock data based on filters
        if "invalid_field" in str(filters):
            raise Exception("Invalid filter field")
        if "Database connection failed" in str(filters):
            raise Exception("Database connection failed")
        
        # Return different data based on filters
        if "channel=ARD" in filters:
            return [
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
                }
            ]
        elif "channel=NonExistent" in filters:
            return []
        else:
            return [
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

# Mock the mtv_dl.mtv_dl module
mock_mtv_dl_module = Mock()
mock_mtv_dl_module.Database = MockDatabase
mock_mtv_dl_module.Downloader = Mock()
sys.modules['mtv_dl.mtv_dl'] = mock_mtv_dl_module

# Now import the main module
import mtv_dl_web.main as main_module
from mtv_dl_web.main import app

# Create test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_database():
    """Reset the app database mock for each test."""
    main_module.db = MockDatabase(None, None)
    yield


def test_search_endpoint_success():
    """Test successful search with valid filters"""
    response = client.post("/api/search", json={"filters": ["channel=ARD"]})
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 1
    assert data["results"][0]["channel"] == "ARD"
    assert data["results"][0]["title"] == "Test Show 1"


def test_search_endpoint_empty_results():
    """Test behavior when no shows match filters"""
    response = client.post("/api/search", json={"filters": ["channel=NonExistent"]})
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 0


def test_search_endpoint_invalid_filters():
    """Test error handling for invalid filters"""
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


def test_search_endpoint_database_error():
    """Test error handling for database errors"""
    response = client.post("/api/search", json={"filters": ["title=Database connection failed"]})
    
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "Database connection failed" in data["detail"]


def test_search_endpoint_multiple_results():
    """Test search returning multiple results"""
    response = client.post("/api/search", json={"filters": ["channel=ZDF"]})
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 2
    
    # Check that we get both channels
    channels = [show["channel"] for show in data["results"]]
    assert "ARD" in channels
    assert "ZDF" in channels


def test_search_response_structure():
    """Test that response has correct structure"""
    response = client.post("/api/search", json={"filters": ["channel=ARD"]})
    data = response.json()
    
    # Check response structure
    assert "results" in data
    result = data["results"][0]
    
    # Verify all expected fields are present
    required_fields = ["hash", "channel", "title", "topic", "size", "start", "duration", "age", "region"]
    for field in required_fields:
        assert field in result, f"Missing required field: {field}"


if __name__ == "__main__":
    print("Running comprehensive search API tests...")
    
    # Run all tests
    test_functions = [
        test_search_endpoint_success,
        test_search_endpoint_empty_results,
        test_search_endpoint_invalid_filters,
        test_search_endpoint_missing_filters,
        test_search_endpoint_database_error,
        test_search_endpoint_multiple_results,
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
