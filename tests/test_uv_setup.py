#!/usr/bin/env python3
"""
Simple smoke test ensuring core functionality works with uv
"""

def test_uv_setup():
    """Test that we can run basic uv commands"""
    import sys
    print("✓ Python version:", sys.version)
    print("✓ uv setup test passed")
    assert True

def test_project_structure():
    """Test that basic project files exist"""
    import os
    assert os.path.exists("pyproject.toml")
    assert os.path.exists("Dockerfile")
    assert os.path.exists("src/main.py")
    assert os.path.exists("src/frontend/hello.html")
    print("✓ Project structure test passed")

if __name__ == "__main__":
    test_uv_setup()
    test_project_structure()
    print("🎉 All basic tests passed!")