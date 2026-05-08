#!/usr/bin/env python3
"""
Test for FastAPI backend initialization (Story 1.1)
"""

import sys
import os
from pathlib import Path

# Add the src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_fastapi_app_initialization():
    """Test that FastAPI app initializes correctly"""
    try:
        from mtv_dl_web.main import app
        
        # Verify app is a FastAPI instance
        assert hasattr(app, 'title'), "FastAPI app should have a title"
        assert hasattr(app, 'version'), "FastAPI app should have a version"
        assert app.title == "MTV Downloader Web Interface", f"Expected title 'MTV Downloader Web Interface', got '{app.title}'"
        assert app.version == "1.0.0", f"Expected version '1.0.0', got '{app.version}'"
        
        print("✓ FastAPI app initialized correctly")
        return True
    except Exception as e:
        print(f"✗ FastAPI app initialization failed: {e}")
        return False

def test_fastapi_routes():
    """Test that basic FastAPI routes are configured"""
    try:
        from mtv_dl_web.main import app
        
        # Check that basic routes exist
        routes = [route.path for route in app.routes]
        
        assert '/' in routes, "Root route should exist"
        assert '/health' in routes, "Health route should exist"
        assert '/api/search' in routes, "Search API route should exist"
        assert '/api/download' in routes, "Download API route should exist"
        
        print("✓ FastAPI routes configured correctly")
        return True
    except Exception as e:
        print(f"✗ FastAPI routes check failed: {e}")
        return False

def test_project_structure():
    """Test that project structure matches requirements"""
    try:
        project_root = Path(__file__).parent.parent
        
        # Check required directories
        required_dirs = [
            'src/mtv_dl_web',
            'src/mtv_dl_web/frontend',
            'src/mtv_dl'
        ]
        
        for dir_path in required_dirs:
            full_path = project_root / dir_path
            assert full_path.exists(), f"Required directory {dir_path} does not exist"
            assert full_path.is_dir(), f"{dir_path} should be a directory"
        
        # Check required files
        required_files = [
            'src/mtv_dl_web/main.py',
            'src/mtv_dl_web/__init__.py',
            'src/__init__.py',
            'src/config.py',
            'src/mtv_dl_web/frontend/hello.html',
            'pyproject.toml'
        ]
        
        for file_path in required_files:
            full_path = project_root / file_path
            assert full_path.exists(), f"Required file {file_path} does not exist"
            assert full_path.is_file(), f"{file_path} should be a file"
        
        print("✓ Project structure matches requirements")
        return True
    except Exception as e:
        print(f"✗ Project structure check failed: {e}")
        return False

def test_dependencies():
    """Test that project dependencies can be imported"""
    try:
        # Test core dependencies
        import fastapi
        import uvicorn
        import pydantic
        
        print("✓ Core dependencies available")
        return True
    except ImportError as e:
        print(f"✗ Dependency import failed: {e}")
        return False

if __name__ == "__main__":
    print("Running tests for Story 1.1: Initialize FastAPI Backend...")
    
    success_count = 0
    total_tests = 4
    
    if test_fastapi_app_initialization():
        success_count += 1
        
    if test_fastapi_routes():
        success_count += 1
        
    if test_project_structure():
        success_count += 1
        
    if test_dependencies():
        success_count += 1
    
    print(f"\nResults: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Story 1.1 implementation is complete.")
        sys.exit(0)
    else:
        print("❌ Some tests failed.")
        sys.exit(1)
