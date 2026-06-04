from pathlib import Path

import pytest

from mtv_dl_web import app as app_module


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
