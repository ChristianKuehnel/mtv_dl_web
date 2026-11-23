from datetime import datetime, timezone
from pathlib import Path
from threading import Event

import pytest

from mtv_dl_web import app as app_module


class FakeWrapper:
    def __init__(self, database_age_errors: int = 0, refresh_result: bool = True):
        self.database_age_errors = database_age_errors
        self.refresh_result = refresh_result
        self.database_age_calls = 0
        self.refresh_database_calls = 0

    def database_age(self) -> datetime:
        self.database_age_calls += 1
        if self.database_age_calls <= self.database_age_errors:
            raise RuntimeError("mtv_dl database age probe failed")
        return datetime(2026, 1, 1, tzinfo=timezone.utc)

    def refresh_database(self) -> bool:
        self.refresh_database_calls += 1
        return self.refresh_result


def test_create_app_exits_when_permission_check_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(app_module, "setup_logging", lambda: None)
    monkeypatch.setattr(app_module.config, "mtv_dl_database_dir", str(tmp_path / "db"))
    monkeypatch.setattr(app_module.config, "base_dir", str(tmp_path / "downloads"))

    def fail_permission_check() -> None:
        raise PermissionError("download_basedir is not writable")

    monkeypatch.setattr(
        app_module.config,
        "validate_runtime_permissions",
        fail_permission_check,
    )

    with pytest.raises(SystemExit) as exc_info:
        app_module.create_app()

    assert exc_info.value.code == 1


def test_ensure_database_available_does_not_refresh_when_probe_succeeds() -> None:
    wrapper = FakeWrapper()

    app_module.ensure_database_available(wrapper)

    assert wrapper.database_age_calls == 1
    assert wrapper.refresh_database_calls == 0


def test_ensure_database_available_refreshes_when_probe_fails() -> None:
    wrapper = FakeWrapper(database_age_errors=1)

    app_module.ensure_database_available(wrapper)

    assert wrapper.database_age_calls == 1
    assert wrapper.refresh_database_calls == 1


def test_ensure_database_available_fails_when_startup_refresh_fails() -> None:
    wrapper = FakeWrapper(database_age_errors=1, refresh_result=False)

    with pytest.raises(RuntimeError, match="startup refresh failed"):
        app_module.ensure_database_available(wrapper)


def test_create_app_exits_when_database_startup_refresh_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(app_module, "setup_logging", lambda: None)
    monkeypatch.setattr(app_module.config, "mtv_dl_database_dir", str(tmp_path / "db"))
    monkeypatch.setattr(app_module.config, "base_dir", str(tmp_path / "downloads"))
    monkeypatch.setattr(app_module.config, "validate_runtime_permissions", lambda: None)
    monkeypatch.setattr(app_module.config, "database_refresh_enabled", False)
    monkeypatch.setattr(
        app_module,
        "Wrapper",
        lambda database_dir, download_path, exclude_audiodeskription: FakeWrapper(
            database_age_errors=1,
            refresh_result=False,
        ),
    )

    with pytest.raises(SystemExit) as exc_info:
        app_module.create_app()

    assert exc_info.value.code == 1


def test_app_stays_live_and_accepts_refresh_when_database_age_probe_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(app_module.config, "mtv_dl_database_dir", str(tmp_path / "db"))
    monkeypatch.setattr(app_module.config, "base_dir", str(tmp_path / "downloads"))
    monkeypatch.setattr(app_module.config, "validate_runtime_permissions", lambda: None)
    monkeypatch.setattr(app_module.config, "database_refresh_enabled", False)
    wrapper = FakeWrapper()
    monkeypatch.setattr(app_module, "Wrapper", lambda *args: wrapper)
    app = app_module.create_app()
    client = app.test_client()

    # Startup succeeds, then the database probe stops working.
    wrapper.database_age_errors = wrapper.database_age_calls + 2
    health = client.get("/health")
    assert health.status_code == 500
    assert health.get_json()["status"] == "error"

    probe_calls = wrapper.database_age_calls
    assert client.get("/livez").status_code == 200
    assert wrapper.database_age_calls == probe_calls
    assert client.get("/").status_code == 200

    refresh = client.get("/refresh_database")
    assert refresh.status_code == 200
    assert refresh.get_json()["status"] == "queued"
    app.download_queue.join()
    assert wrapper.refresh_database_calls == 1


def test_health_skips_database_age_during_refresh_and_resumes_afterward(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(app_module.config, "mtv_dl_database_dir", str(tmp_path / "db"))
    monkeypatch.setattr(app_module.config, "base_dir", str(tmp_path / "downloads"))
    monkeypatch.setattr(app_module.config, "validate_runtime_permissions", lambda: None)
    monkeypatch.setattr(app_module.config, "database_refresh_enabled", False)
    wrapper = FakeWrapper()
    started = Event()
    finish = Event()

    def refresh_database() -> bool:
        started.set()
        return finish.wait(timeout=5)

    monkeypatch.setattr(wrapper, "refresh_database", refresh_database)
    monkeypatch.setattr(app_module, "Wrapper", lambda *args: wrapper)
    app = app_module.create_app()
    client = app.test_client()

    probe_calls = wrapper.database_age_calls
    wrapper.database_age_errors = probe_calls + 1
    try:
        assert client.get("/refresh_database").status_code == 200
        assert started.wait(timeout=5)
        health = client.get("/health")
        assert health.status_code == 200
        assert health.get_json() == {"status": "refreshing"}
        assert wrapper.database_age_calls == probe_calls
    finally:
        finish.set()
        app.download_queue.join()

    wrapper.database_age_errors = 0
    health = client.get("/health")
    assert health.status_code == 200
    assert health.get_json() == {
        "status": "ok",
        "last_db_update": "2026-01-01T00:00:00+00:00",
    }
    assert wrapper.database_age_calls == probe_calls + 1
