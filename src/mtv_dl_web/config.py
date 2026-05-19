"""Configuration values loaded from ``mtv_dl_web.yaml``."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Callable, Mapping

import yaml


logger = logging.getLogger(__name__)

CONFIG_PATH = Path(
    os.environ.get(
        "MTV_DL_WEB_CONFIG",
        Path(__file__).resolve().parents[2] / "mtv_dl_web.yaml",
    )
)

ENV_PREFIX = "MTV_DL_WEB_"


def _parse_bool(value: str) -> bool:
    normalized_value = value.strip().lower()
    if normalized_value in {"1", "true", "yes", "on"}:
        return True
    if normalized_value in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"Invalid boolean value: {value!r}")


def _apply_environment_overrides(
    config: dict[str, Any], environ: Mapping[str, str]
) -> dict[str, Any]:
    config = dict(config)
    database_refresh_config = config.get("database_refresh", {})
    if not isinstance(database_refresh_config, dict):
        raise ValueError("database_refresh must be a YAML mapping")

    config["database_refresh"] = dict(database_refresh_config)
    overrides: tuple[tuple[str, tuple[str, ...], Callable[[str], Any]], ...] = (
        ("MTV_DL_WEB_MTV_DL_DATABASE_DIR", ("mtv_dl_database_dir",), str),
        ("MTV_DL_WEB_HOST", ("host",), str),
        ("MTV_DL_WEB_PORT", ("port",), int),
        ("MTV_DL_WEB_LOGGING_LEVEL", ("logging_level",), str),
        ("MTV_DL_WEB_DOWNLOAD_BASEDIR", ("download_basedir",), str),
        ("MTV_DL_WEB_MTV_DL_TARGETDIR", ("mtv_dl_targetdir",), str),
        (
            "MTV_DL_WEB_DATABASE_REFRESH_ENABLED",
            ("database_refresh", "enabled"),
            _parse_bool,
        ),
        (
            "MTV_DL_WEB_DATABASE_REFRESH_CRON",
            ("database_refresh", "cron"),
            str,
        ),
        (
            "MTV_DL_WEB_DATABASE_REFRESH_TIMEZONE",
            ("database_refresh", "timezone"),
            str,
        ),
    )

    for env_name, path, parser in overrides:
        if env_name not in environ:
            continue

        parsed_value = parser(environ[env_name])
        if len(path) == 1:
            config[path[0]] = parsed_value
        else:
            nested_config = config[path[0]]
            if not isinstance(nested_config, dict):
                raise ValueError(f"{path[0]} must be a YAML mapping")
            nested_config[path[1]] = parsed_value

    return config


def _load_config(
    path: Path = CONFIG_PATH, environ: Mapping[str, str] = os.environ
) -> dict[str, Any]:
    logger.debug("Loading configuration from %s", path)

    with path.open(encoding="utf-8") as config_file:
        loaded_config = yaml.safe_load(config_file)

    if not isinstance(loaded_config, dict):
        raise ValueError(f"Config file must contain a YAML mapping: {path}")

    config: dict[str, Any] = loaded_config
    config = _apply_environment_overrides(config, environ)
    logger.debug("Loaded configuration keys: %s", sorted(config))
    return config


def _normalize_base_dir(base_dir: str) -> str:
    base_dir = base_dir.rstrip("/\\")

    if not base_dir:
        return ""

    return os.path.abspath(os.path.expanduser(base_dir))


def _join_download_path(base_dir: str, target_dir: str) -> str:
    target_dir = target_dir.lstrip("/\\")

    if not target_dir:
        return base_dir

    return os.path.join(base_dir, target_dir)


config = _load_config()
database_refresh_config = config.get("database_refresh", {})
if not isinstance(database_refresh_config, dict):
    raise ValueError("database_refresh must be a YAML mapping")

mtv_dl_database_dir: str = str(config["mtv_dl_database_dir"])
download_basedir: str = str(config["download_basedir"])
mtv_dl_targetdir: str = str(config["mtv_dl_targetdir"])
base_dir: str = _normalize_base_dir(download_basedir)
download_path: str = _join_download_path(base_dir, mtv_dl_targetdir)
host: str = str(config["host"])
port: int = int(config["port"])
logging_level: str = str(config["logging_level"])
database_refresh_enabled: bool = bool(database_refresh_config.get("enabled", False))
database_refresh_cron: str = str(database_refresh_config.get("cron", ""))
database_refresh_timezone: str = str(database_refresh_config.get("timezone", "UTC"))


__all__ = [
    "CONFIG_PATH",
    "base_dir",
    "config",
    "database_refresh_config",
    "database_refresh_cron",
    "database_refresh_enabled",
    "database_refresh_timezone",
    "download_basedir",
    "download_path",
    "host",
    "logging_level",
    "mtv_dl_database_dir",
    "mtv_dl_targetdir",
    "port",
]
