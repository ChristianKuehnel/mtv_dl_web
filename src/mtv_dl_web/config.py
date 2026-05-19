"""Configuration values loaded from ``mtv_dl_web.yaml``."""

from __future__ import annotations

import ast
import logging
import os
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)

CONFIG_PATH = Path(
    os.environ.get(
        "MTV_DL_WEB_CONFIG",
        Path(__file__).resolve().parents[2] / "mtv_dl_web.yaml",
    )
)


def _parse_value(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""

    try:
        return ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return value


def _load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    config: dict[str, Any] = {}
    logger.debug("Loading configuration from %s", path)

    with path.open(encoding="utf-8") as config_file:
        for line_number, line in enumerate(config_file, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            key, separator, value = stripped.partition(":")
            if not separator:
                raise ValueError(f"Invalid config line {line_number}: {line.rstrip()}")

            config[key.strip()] = _parse_value(value)

    logger.debug("Loaded configuration keys: %s", sorted(config))
    return config


config = _load_config()

mtv_dl_database_dir: str = str(config["mtv_dl_database_dir"])
host: str = str(config["host"])
port: int = int(config["port"])
logging_level: str = str(config["logging_level"])


__all__ = [
    "CONFIG_PATH",
    "config",
    "host",
    "logging_level",
    "mtv_dl_database_dir",
    "port",
]
