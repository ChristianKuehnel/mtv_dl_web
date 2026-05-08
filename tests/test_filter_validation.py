#!/usr/bin/env python3
"""
Comprehensive test suite for filter validation in the search API endpoint
Tests all filter validation scenarios including valid and invalid operators/fields
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock the mtv_dl module to avoid dependency issues
from unittest.mock import Mock
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
        # Mock method - return empty list to avoid database errors
        return []

# Patch the Database import
sys.modules['mtv_dl.mtv_dl'].Database = MockDatabase

from mtv_dl_web.main import app

# Create test client
client = TestClient(app)


def test_valid_operators():
    """Test that all supported operators are accepted"""
    valid_operators = ["=", "!=", "+", "-"]
    
    for operator in valid_operators:
        response = client.post("/api/search", json={"filters": [f"channel{operator}ARD"]})
        # Should return 200 because validation passes and mock database returns empty list
        assert response.status_code == 200
        

def test_valid_fields():
    """Test that all supported fields are accepted"""
    valid_fields = [
        "description", "region", "size", "channel", "topic", "title", "hash", "url",
        "duration", "age", "start", "dow", "hour", "minute", "season", "episode"
    ]
    
    for field in valid_fields:
        response = client.post("/api/search", json={"filters": [f"{field}=test"]})
        # Should return 200 because validation passes and mock database returns empty list
        assert response.status_code == 200
        

def test_invalid_operators():
    """Test that unsupported operators are rejected with 400"""
    invalid_operators = ["<", ">", "<=", ">=", "~", "@", "#"]
    
    for operator in invalid_operators:
        response = client.post("/api/search", json={"filters": [f"channel{operator}ARD"]})
        
        # Should return 400 Bad Request for invalid operator
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Unsupported operator" in data["detail"]
        assert operator in data["detail"]
        

def test_invalid_fields():
    """Test that unsupported fields are rejected with 400"""
    invalid_fields = ["invalid_field", "unknown", "test", "name", "author", "date"]
    
    for field in invalid_fields:
        response = client.post("/api/search", json={"filters": [f"{field}=test"]})
        
        # Should return 400 Bad Request for invalid field
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Unsupported field" in data["detail"]
        assert field in data["detail"]
        

def test_url_field_mapping():
    """Test that 'url' field is properly mapped to 'url_http'"""
    # This should work because 'url' gets mapped to 'url_http' internally
    response = client.post("/api/search", json={"filters": ["url=http://example.com"]})
    # Should return 200 because validation passes and mock database returns empty list
    assert response.status_code == 200
    

def test_complex_valid_filters():
    """Test complex filter combinations with valid operators and fields"""
    valid_filters = [
        "channel=ARD",
        "title+News",
        "duration-30m",
        "age!=7d",
        "topic=Documentary"
    ]
    
    response = client.post("/api/search", json={"filters": valid_filters})
    # Should return 200 because validation passes and mock database returns empty list
    assert response.status_code == 200
    

def test_mixed_valid_invalid_filters():
    """Test that a single invalid filter in a list causes rejection"""
    mixed_filters = [
        "channel=ARD",  # valid
        "invalid_field=test",  # invalid
        "title+News"  # valid
    ]
    
    response = client.post("/api/search", json={"filters": mixed_filters})
    
    # Should return 400 because of the invalid field
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Unsupported field" in data["detail"]
    assert "invalid_field" in data["detail"]
    

def test_invalid_filter_format():
    """Test that malformed filters are rejected"""
    invalid_formats = [
        "malformed_filter",  # no operator
        "=ARD",  # no field
        "channel",  # no value
        "",  # empty string
        # Note: "channel==ARD" is actually valid - it searches for channel="=ARD"
        # This is because the regex matches "=" as operator and "=ARD" as pattern
    ]
    
    for invalid_filter in invalid_formats:
        response = client.post("/api/search", json={"filters": [invalid_filter]})
        
        # Should return 400 for invalid format
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Invalid filter format" in data["detail"]
        

def test_all_supported_operator_field_combinations():
    """Test various combinations of supported operators and fields"""
    test_cases = [
        # Format: (field, operator, value)
        ("channel", "=", "ARD"),
        ("title", "!=", "News"),
        ("duration", "+", "30m"),
        ("size", "-", "100"),
        ("topic", "=", "Documentary"),
        ("region", "!=", "DE"),
        ("age", "+", "7d"),
        ("start", "=", "2023-01-01"),
        ("dow", "=", "1"),
        ("hour", "=", "12"),
        ("minute", "=", "30"),
        ("season", "=", "1"),
        ("episode", "=", "5"),
        ("hash", "!=", "abc123"),
        ("url", "=", "http://example.com"),
        ("description", "+", "test"),
    ]
    
    for field, operator, value in test_cases:
        filter_str = f"{field}{operator}{value}"
        response = client.post("/api/search", json={"filters": [filter_str]})
        
        # Should return 200 because validation passes and mock database returns empty list
        assert response.status_code == 200
        

def test_empty_filters_list():
    """Test that empty filters list is handled correctly"""
    response = client.post("/api/search", json={"filters": []})
    
    # Empty filters should be valid (no validation error)
    # Should return 200 because validation passes and mock database returns empty list
    assert response.status_code == 200
    

def test_validation_error_message_format():
    """Test that validation error messages include helpful information"""
    response = client.post("/api/search", json={"filters": ["invalid_field=test"]})
    
    assert response.status_code == 400
    data = response.json()
    
    # Check that error message includes helpful details
    assert "detail" in data
    error_detail = data["detail"]
    
    # Should mention the invalid field
    assert "invalid_field" in error_detail
    
    # Should list supported fields
    assert "Supported fields" in error_detail
    
    # Should include the full filter string for context
    assert "invalid_field=test" in error_detail


if __name__ == "__main__":
    print("Running comprehensive filter validation tests...")
    
    # Run all tests
    test_functions = [
        test_valid_operators,
        test_valid_fields,
        test_invalid_operators,
        test_invalid_fields,
        test_url_field_mapping,
        test_complex_valid_filters,
        test_mixed_valid_invalid_filters,
        test_invalid_filter_format,
        test_all_supported_operator_field_combinations,
        test_empty_filters_list,
        test_validation_error_message_format
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
        print("🎉 All filter validation tests passed!")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the implementation.")
        sys.exit(1)