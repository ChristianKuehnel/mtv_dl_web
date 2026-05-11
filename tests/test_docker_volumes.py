#!/usr/bin/env python3
"""
Test for Docker volume configuration (Story 1.3)
"""

from pathlib import Path


def test_dockerfile_volumes():
    """Test that Dockerfile has proper volume setup"""
    dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
    content = dockerfile_path.read_text()

    assert "mkdir -p /data /downloads /config" in content
    assert "mtv_dl_web.main:app" in content
    assert "chown -R appuser:appuser /app /data /downloads /config" in content


def test_docker_compose_volumes():
    """Test that docker-compose.yml has proper volume configuration"""
    compose_path = Path(__file__).parent.parent / "docker-compose.yml"
    assert compose_path.exists()

    content = compose_path.read_text()

    required_volumes = ["/data", "/downloads", "/config", "/home/appuser/.mtv_dl_web"]
    for volume in required_volumes:
        assert volume in content

    assert "mtv_dl_web:" in content
    assert "ports:" in content
    assert "8000:8000" in content


def test_volume_paths_architecture():
    """Test that volume paths match architecture requirements"""
    compose_path = Path(__file__).parent.parent / "docker-compose.yml"
    content = compose_path.read_text()

    assert "/home/appuser/.mtv_dl_web" in content
    assert "/data" in content
    assert "/downloads" in content
    assert "/config" in content
