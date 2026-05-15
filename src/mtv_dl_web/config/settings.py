# Basic Configuration for MTV Downloader Web

import os
import logging
from pathlib import Path
from typing import Any, Optional

from pydantic.v1 import BaseSettings, Field
import yaml

logger = logging.getLogger(__name__)
ENV_PREFIX = "mtv_dl_web"


def env_key(name: str) -> str:
    return f"{ENV_PREFIX}.{name}"


class Settings(BaseSettings):
    # Service configuration
    port: int = Field(8000, env=env_key("port"))
    host: str = Field("localhost", env=env_key("host"))

    # Database configuration
    database_path: str = Field(os.path.expanduser("~/.mtv_dl_web"), env=env_key("database_path"))

    # Download configuration
    download_quality: str = Field("best", env=env_key("download_quality"))
    target_directory: str = Field("/downloads", env=env_key("target_directory"))

    # Feature flags
    enable_subtitles: bool = Field(True, env=env_key("enable_subtitles"))
    enable_nfo: bool = Field(True, env=env_key("enable_nfo"))
    enable_mkv_merge: bool = Field(False, env=env_key("enable_mkv_merge"))

    # Configuration file path
    config_file: Optional[str] = Field(None, env=env_key("config_file"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @classmethod
    def load_from_file(cls, config_file_path: str) -> "Settings":
        """Load settings from a YAML file."""
        if not os.path.exists(config_file_path):
            raise ValueError(f"Config file does not exist: {config_file_path}")

        with open(config_file_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        if config_data is None:
            config_data = {}

        if not isinstance(config_data, dict):
            raise ValueError("Configuration file must contain a YAML mapping at the top level")

        unknown_keys = sorted(key for key in config_data if key not in cls.__fields__)
        if unknown_keys:
            raise ValueError(f"Unknown configuration keys: {', '.join(unknown_keys)}")

        settings = cls()
        merged_values = settings.dict()
        env_override_fields = settings.__fields_set__

        for key, value in config_data.items():
            if key not in env_override_fields:
                merged_values[key] = value

        return cls(**merged_values)


# Load settings
# Try to load from config file if specified, otherwise use defaults
bootstrap_settings = Settings()
config_file_path = bootstrap_settings.config_file
if config_file_path:
    try:
        settings = Settings.load_from_file(config_file_path)
    except Exception as e:
        logger.error("Failed to load configuration from %s: %s", config_file_path, e)
        raise SystemExit(f"Failed to load configuration from {config_file_path}: {e}")
else:
    settings = Settings()
