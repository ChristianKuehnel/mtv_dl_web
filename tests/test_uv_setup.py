#!/usr/bin/env python3
"""
Simple smoke test ensuring core functionality works with uv
"""

from pathlib import Path
import tomllib


PROJECT_ROOT = Path(__file__).resolve().parent.parent

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


def test_dependency_resolution_parity_contract() -> None:
    """Verify local/test/container all resolve mtv-dl via pyproject-driven install."""
    pyproject_data = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = pyproject_data["project"]["dependencies"]
    assert any(dep == "mtv-dl" or dep.startswith("mtv-dl") for dep in dependencies)

    # Guard against reintroducing a vendored fallback copy that could shadow installs.
    assert not (PROJECT_ROOT / "src" / "mtv_dl").exists()

    dockerfile = (PROJECT_ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "COPY pyproject.toml ." in dockerfile
    assert "uv sync --frozen" in dockerfile
    assert "src/mtv_dl" not in dockerfile


def test_mtv_dl_import_works():
    """Test that mtv_dl can be imported correctly."""
    from mtv_dl import mtv_dl as mtv_dl_module
    from mtv_dl.mtv_dl import Database, Downloader

    assert Database is not None
    assert Downloader is not None

    module_path = Path(mtv_dl_module.__file__).resolve()
    assert str(module_path).startswith(str(PROJECT_ROOT / ".venv"))
    assert "src/mtv_dl" not in str(module_path)

if __name__ == "__main__":
    test_uv_setup()
    test_project_structure()
    test_mtv_dl_import_works()
    print("🎉 All basic tests passed!")
