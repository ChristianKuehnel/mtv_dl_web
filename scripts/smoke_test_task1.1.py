#!/usr/bin/env python3
"""
Simple smoke test for Task 1.1 Implementation - Refactored for pytest
"""

import sys
import os

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi.testclient import TestClient
from main import app


def test_hello_world_page():
    """Test that hello world page is served"""
    client = TestClient(app)
    
    response = client.get("/")
    
    if response.status_code == 200:
        if "Hello World" in response.text:
            print("✓ Hello World page test PASSED")
            return True
        else:
            print("✗ Hello World page test FAILED - Content mismatch")
            return False
    else:
        print(f"✗ Hello World page test FAILED - Status code: {response.status_code}")
        return False


def test_health_endpoint():
    """Test that health endpoint returns 200"""
    client = TestClient(app)
    
    response = client.get("/health")
    
    if response.status_code == 200:
        print("✓ Health endpoint test PASSED")
        return True
    else:
        print(f"✗ Health endpoint test FAILED - Status code: {response.status_code}")
        return False


if __name__ == "__main__":
    print("Running smoke tests for Task 1.1...")
    
    success_count = 0
    total_tests = 2
    
    if test_hello_world_page():
        success_count += 1
        
    if test_health_endpoint():
        success_count += 1
        
    print(f"\nResults: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Task 1.1 implementation is working.")
        sys.exit(0)
    else:
        print("❌ Some tests failed.")
        sys.exit(1)
