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
