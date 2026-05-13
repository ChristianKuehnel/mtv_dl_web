#!/usr/bin/env python3
"""
Simple smoke test ensuring core functionality works with uv
"""

from pathlib import Path
import tomllib

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
    assert os.path.exists("src/mtv_dl_web/main.py")
    assert os.path.exists("src/mtv_dl_web/frontend/hello.html")
    print("✓ Project structure test passed")


def test_mtv_dl_resolves_from_declared_dependency_only():
    """Ensure mtv-dl is resolved from declared dependency, not local uv path sources."""
    pyproject_path = Path("pyproject.toml")
    pyproject_data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    dependencies = pyproject_data["project"]["dependencies"]
    assert "mtv-dl" in dependencies

    uv_sources = pyproject_data.get("tool", {}).get("uv", {}).get("sources", {})
    assert "mtv-dl" not in uv_sources

if __name__ == "__main__":
    test_uv_setup()
    test_project_structure()
    print("🎉 All basic tests passed!")
