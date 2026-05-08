#!/usr/bin/env python3
"""
Comprehensive test suite for the search API endpoint
Tests all search functionality including success cases, error handling, and edge cases
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mtv_dl_web.main import app
from mtv_dl.mtv_dl import Database

# Create test client
client = TestClient(app)


def test_search_endpoint_success():
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
    
    with patch.object(Database, 'filtered') as mock_filtered:
        mock_filtered.return_value = mock_shows
        
        response = client.post("/api/search", json={"filters": ["channel=ARD"]})
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 2
        assert data["results"][0]["channel"] == "ARD"
        assert data["results"][1]["channel"] == "ZDF"


def test_search_endpoint_empty_results():
    """Test behavior when no shows match filters"""
    with patch.object(Database, 'filtered') as mock_filtered:
        mock_filtered.return_value = []
        
        response = client.post("/api/search", json={"filters": ["channel=NonExistent"]})
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 0


def test_search_endpoint_invalid_filters():
    """Test error handling for invalid filters"""
    with patch.object(Database, 'filtered') as mock_filtered:
        mock_filtered.side_effect = Exception("Invalid filter field")
        
        response = client.post("/api/search", json={"filters": ["invalid_field=value"]})
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Invalid filter field" in data["detail"]


def test_search_endpoint_missing_filters():
    """Test error handling when filters are missing"""
    response = client.post("/api/search", json={})
    
    assert response.status_code == 422  # FastAPI validation error
    data = response.json()
    assert "detail" in data


def test_search_endpoint_database_error():
    """Test error handling for database errors"""
    with patch.object(Database, 'filtered') as mock_filtered:
        mock_filtered.side_effect = Exception("Database connection failed")
        
        response = client.post("/api/search", json={"filters": ["channel=ARD"]})
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Database connection failed" in data["detail"]


def test_search_endpoint_complex_filters():
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
    
    with patch.object(Database, 'filtered') as mock_filtered:
        mock_filtered.return_value = mock_shows
        
        # Test with multiple filters
        response = client.post("/api/search", json={
            "filters": ["channel=ARD", "topic='extra 3'", "duration+20m"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["title"] == "Extra 3"


def test_search_endpoint_special_characters():
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
    
    with patch.object(Database, 'filtered') as mock_filtered:
        mock_filtered.return_value = mock_shows
        
        response = client.post("/api/search", json={
            "filters": ["title='Show with \\'quotes\\' and spaces'"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1


def test_search_response_structure():
    """Test that response has correct structure"""
    mock_shows = [
        {
            "hash": "test1",
            "channel": "ARD",
            "title": "Test Show",
            "topic": "News", 
            "size": 100,
            "start": "2023-01-01T12:00:00",
            "duration": "30m",
            "age": "7d",
            "region": "DE",
            "downloaded": None
        }
    ]
    
    with patch.object(Database, 'filtered') as mock_filtered:
        mock_filtered.return_value = mock_shows
        
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