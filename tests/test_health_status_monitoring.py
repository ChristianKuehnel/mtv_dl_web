#!/usr/bin/env python3
"""
Tests for Story 1.5: Improve Health Status Monitoring
"""

import importlib
import sys
import time
from collections.abc import Iterator
from math import ceil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import mtv_dl_web.main as main_module

main_module = importlib.reload(main_module)
client = TestClient(main_module.app)


class HealthyCursor:
    def execute(self, query: str) -> None:
        assert query == "SELECT 1"

    def fetchone(self) -> tuple[int]:
        return (1,)


class HealthyConnection:
    def __enter__(self) -> "HealthyConnection":
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        pass

    def cursor(self) -> HealthyCursor:
        return HealthyCursor()


class HealthyDatabase:
    connection = HealthyConnection()

    def __init__(self, database_file: Path, history_file: Path) -> None:
        self.database_file = database_file
        self.history_file = history_file

    def update_if_old(self) -> None:
        pass


@pytest.fixture(autouse=True)
def health_database(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setattr(main_module, "Database", HealthyDatabase)
    main_module._database_update_count = 0
    yield
    main_module._database_update_count = 0


def test_health_reports_healthy_when_database_is_not_updating() -> None:
    main_module.set_database_update_in_progress(False)

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert "database" in payload


def test_health_reports_updating_while_database_refresh_is_running() -> None:
    main_module.set_database_update_in_progress(True)

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "updating"
    assert "database" in payload

    main_module.set_database_update_in_progress(False)


def test_health_check_completes_within_one_second() -> None:
    durations: list[float] = []

    for _ in range(20):
        start_time = time.perf_counter()
        response = client.get("/health")
        elapsed = time.perf_counter() - start_time

        assert response.status_code == 200
        durations.append(elapsed)

    durations.sort()
    p95_index = max(0, ceil(len(durations) * 0.95) - 1)
    p95_duration = durations[p95_index]
    assert p95_duration < 1.0


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


def test_database_refresh_state_tracks_overlapping_updates() -> None:
    main_module.set_database_update_in_progress(False)

    main_module.set_database_update_in_progress(True)
    main_module.set_database_update_in_progress(True)
    main_module.set_database_update_in_progress(False)

    assert main_module.is_database_update_in_progress() is True

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "updating"
    assert "database" in payload

    main_module.set_database_update_in_progress(False)

    assert main_module.is_database_update_in_progress() is False


def test_health_reports_unhealthy_when_database_query_fails(monkeypatch) -> None:
    class BrokenCursor:
        def execute(self, query: str) -> None:
            raise RuntimeError("database is unavailable")

        def fetchone(self) -> tuple[int]:
            return (1,)

    class BrokenConnection:
        def __enter__(self) -> "BrokenConnection":
            return self

        def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
            pass

        def cursor(self) -> BrokenCursor:
            return BrokenCursor()

    class BrokenDatabase:
        connection = BrokenConnection()

        def __init__(self, database_file: Path, history_file: Path) -> None:
            self.database_file = database_file
            self.history_file = history_file

    monkeypatch.setattr(main_module, "Database", BrokenDatabase)
    main_module.set_database_update_in_progress(False)

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "unhealthy"
    assert "database" in payload


def test_frontend_contains_three_state_health_indicator() -> None:
    html = (Path(__file__).parent.parent / "src" / "mtv_dl_web" / "frontend" / "index.html").read_text()

    assert 'id="health-indicator"' in html
    assert 'id="health-dot"' in html
    assert 'id="health-label"' in html
    assert "updateHealthStatus" in html
    assert 'online: {' in html
    assert 'label: "online"' in html
    assert 'dotClass: "h-2.5 w-2.5 rounded-full bg-green-500"' in html
    assert 'border border-green-200 bg-green-50' in html
    assert 'updating: {' in html
    assert 'label: "updating"' in html
    assert 'dotClass: "h-2.5 w-2.5 rounded-full bg-yellow-500"' in html
    assert 'border border-yellow-200 bg-yellow-50' in html
    assert 'offline: {' in html
    assert 'label: "offline"' in html
    assert 'dotClass: "h-2.5 w-2.5 rounded-full bg-red-500"' in html
    assert 'border border-red-200 bg-red-50' in html
    assert "/health" in html
