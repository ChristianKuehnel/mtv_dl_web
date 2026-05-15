#!/usr/bin/env python3
"""Tests for Story 1.4 service configuration behavior."""

from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mtv_dl_web.config.settings import Settings


def test_env_overrides_yaml_values(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Environment values must take precedence over YAML values."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("port: 7000\ntarget_directory: /tmp/from-file\n", encoding="utf-8")

    monkeypatch.setenv("PORT", "9001")

    loaded = Settings.load_from_file(str(config_file))

    assert loaded.port == 9001
    assert loaded.target_directory == "/tmp/from-file"


def test_invalid_yaml_top_level_is_rejected(tmp_path: Path) -> None:
    """Configuration must be a YAML mapping."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("- not\n- a\n- mapping\n", encoding="utf-8")

    with pytest.raises(ValueError, match="YAML mapping"):
        Settings.load_from_file(str(config_file))


def test_unknown_keys_are_rejected(tmp_path: Path) -> None:
    """Unknown config keys should fail fast with a clear error."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("unknown_setting: true\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Unknown configuration keys"):
        Settings.load_from_file(str(config_file))


def test_every_setting_uses_file_when_env_not_set(tmp_path: Path) -> None:
    """All configurable settings should be sourced from YAML when env is absent."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "\n".join(
            [
                "port: 7001",
                "host: 127.0.0.1",
                "database_path: /tmp/test-db",
                "download_quality: low",
                "target_directory: /tmp/downloads",
                "enable_subtitles: false",
                "enable_nfo: false",
                "enable_mkv_merge: true",
                "config_file: /config/custom.yaml",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    loaded = Settings.load_from_file(str(config_file))

    assert loaded.port == 7001
    assert loaded.host == "127.0.0.1"
    assert loaded.database_path == "/tmp/test-db"
    assert loaded.download_quality == "low"
    assert loaded.target_directory == "/tmp/downloads"
    assert loaded.enable_subtitles is False
    assert loaded.enable_nfo is False
    assert loaded.enable_mkv_merge is True
    assert loaded.config_file == "/config/custom.yaml"


def test_every_setting_uses_env_over_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Environment variables must override YAML for every supported setting."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "\n".join(
            [
                "port: 7001",
                "host: 127.0.0.1",
                "database_path: /tmp/test-db",
                "download_quality: low",
                "target_directory: /tmp/downloads",
                "enable_subtitles: false",
                "enable_nfo: false",
                "enable_mkv_merge: true",
                "config_file: /config/custom.yaml",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("PORT", "9001")
    monkeypatch.setenv("HOST", "0.0.0.0")
    monkeypatch.setenv("DATABASE_PATH", "/env/db")
    monkeypatch.setenv("DOWNLOAD_QUALITY", "best")
    monkeypatch.setenv("TARGET_DIRECTORY", "/env/downloads")
    monkeypatch.setenv("ENABLE_SUBTITLES", "true")
    monkeypatch.setenv("ENABLE_NFO", "true")
    monkeypatch.setenv("ENABLE_MKV_MERGE", "false")
    monkeypatch.setenv("CONFIG_FILE", "/env/config.yaml")

    loaded = Settings.load_from_file(str(config_file))

    assert loaded.port == 9001
    assert loaded.host == "0.0.0.0"
    assert loaded.database_path == "/env/db"
    assert loaded.download_quality == "best"
    assert loaded.target_directory == "/env/downloads"
    assert loaded.enable_subtitles is True
    assert loaded.enable_nfo is True
    assert loaded.enable_mkv_merge is False
    assert loaded.config_file == "/env/config.yaml"


def test_invalid_env_type_raises_validation_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Invalid env value types should fail validation at settings construction."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("port: 7000\n", encoding="utf-8")

    monkeypatch.setenv("PORT", "not-an-int")

    with pytest.raises(ValueError, match="port"):
        Settings.load_from_file(str(config_file))


def test_default_fallback_when_absent_from_env_and_file(tmp_path: Path) -> None:
    """Missing fields in env and YAML should keep in-code defaults."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("port: 7000\n", encoding="utf-8")

    loaded = Settings.load_from_file(str(config_file))

    assert loaded.enable_mkv_merge is False
