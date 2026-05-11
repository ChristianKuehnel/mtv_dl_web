#!/usr/bin/env python3
"""
Tests for Story 1.5: Improve Health Status Monitoring
"""

import importlib
import sys
import time
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import mtv_dl_web.main as main_module

main_module = importlib.reload(main_module)
client = TestClient(main_module.app)


def test_health_reports_healthy_when_database_is_not_updating() -> None:
    main_module.set_database_update_in_progress(False)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_health_reports_updating_while_database_refresh_is_running() -> None:
    main_module.set_database_update_in_progress(True)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "updating"}

    main_module.set_database_update_in_progress(False)


def test_health_check_completes_within_one_second() -> None:
    start_time = time.perf_counter()

    response = client.get("/health")

    elapsed = time.perf_counter() - start_time
    assert response.status_code == 200
    assert elapsed < 1.0


def test_database_refresh_state_is_reset_after_connection_update(monkeypatch) -> None:
    class UpdatingDatabase:
        def __init__(self, database_file: Path, history_file: Path) -> None:
            self.database_file = database_file
            self.history_file = history_file

        def update_if_old(self) -> None:
            assert main_module.is_database_update_in_progress() is True

    monkeypatch.setattr(main_module, "Database", UpdatingDatabase)
    main_module.set_database_update_in_progress(False)

    main_module.get_db_connection()

    assert main_module.is_database_update_in_progress() is False


def test_frontend_contains_three_state_health_indicator() -> None:
    html = (Path(__file__).parent.parent / "src" / "mtv_dl_web" / "frontend" / "index.html").read_text()

    assert 'id="health-indicator"' in html
    assert 'id="health-dot"' in html
    assert 'id="health-label"' in html
    assert "updateHealthStatus" in html
    assert '"online"' in html
    assert '"updating"' in html
    assert '"offline"' in html
    assert "/health" in html
