#!/usr/bin/env python3
"""
Simple smoke test ensuring core functionality works
"""

from pathlib import Path


def test_basic_imports():
    """Test that we can import the main module without major issues"""
    import mtv_dl_web.main as main

    assert hasattr(main, "app")


def test_hello_html_exists():
    """Test that our hello.html file exists and has correct content"""
    html_file = Path(__file__).parent.parent / "src" / "mtv_dl_web" / "frontend" / "hello.html"
    content = html_file.read_text()

    assert "Hello World" in content
    assert "Welcome to the MTV Downloader Web Interface" in content


def test_simple_functionality():
    """Test the basic functionality we've implemented"""
    import mtv_dl_web.main as main

    assert main.app.title == "MTV Downloader Web Interface"
