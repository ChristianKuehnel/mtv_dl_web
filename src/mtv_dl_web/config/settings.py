# Basic Configuration for MTV Downloader Web

import os
import logging
from pathlib import Path
from typing import Any, Optional

from pydantic.v1 import BaseSettings
import yaml


logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # Service configuration
    port: int = 8000
    host: str = "0.0.0.0"

    # Database configuration
    database_path: str = os.path.expanduser("~/.mtv_dl_web")

    # Download configuration
    download_quality: str = "best"
    target_directory: str = os.path.expanduser("~/Downloads/mtv_dl")

    # Feature flags
    enable_subtitles: bool = True
    enable_nfo: bool = True
    enable_mkv_merge: bool = False

    # Configuration file path
    config_file: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

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
        for key, value in config_data.items():
            if key.upper() not in os.environ:
                setattr(settings, key, value)

        return settings


# Load settings
# Try to load from config file if specified, otherwise use defaults
config_file_path = os.environ.get('CONFIG_FILE', None)
if config_file_path:
    try:
        settings = Settings.load_from_file(config_file_path)
    except Exception as e:
        logger.error("Failed to load configuration from %s: %s", config_file_path, e)
        raise SystemExit(f"Failed to load configuration from {config_file_path}: {e}")
else:
    settings = Settings()

# Validate that target directory exists (only if it's not overridden by environment or config)
# We need to handle the case where the YAML file might override the default
# Get the original default value for comparison
original_target_directory = os.path.expanduser("~/Downloads/mtv_dl")
if (
    not os.environ.get("TARGET_DIRECTORY")
    and not os.environ.get("CONFIG_FILE")
    and settings.target_directory == original_target_directory
    and not Path(settings.target_directory).exists()
):
    # If it's the default and doesn't exist, create it or raise error
    raise SystemExit(
        f"Error: Target directory '{settings.target_directory}' does not exist. Please create it or update the configuration."
    )
