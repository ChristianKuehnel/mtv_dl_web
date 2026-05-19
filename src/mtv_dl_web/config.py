"""Configuration values loaded from ``mtv_dl_web.yaml``."""

from __future__ import annotations

import ast
import os
from pathlib import Path
from typing import Any


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

    with path.open(encoding="utf-8") as config_file:
        for line_number, line in enumerate(config_file, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            key, separator, value = stripped.partition(":")
            if not separator:
                raise ValueError(f"Invalid config line {line_number}: {line.rstrip()}")

            config[key.strip()] = _parse_value(value)

    return config


config = _load_config()

mtv_dl_database_dir: str = str(config["mtv_dl_database_dir"])
host: str = str(config["host"])
port: int = int(config["port"])


__all__ = ["CONFIG_PATH", "config", "host", "mtv_dl_database_dir", "port"]
