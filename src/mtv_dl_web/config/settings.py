# Basic Configuration for MTV Downloader Web

import os
from pathlib import Path

from pydantic.v1 import BaseSettings


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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Load settings
settings = Settings()

# Validate that target directory exists (only if it's not overridden by environment)
# We need to handle the case where the YAML file might override the default
# Get the original default value for comparison
original_target_directory = os.path.expanduser("~/Downloads/mtv_dl")
if (
    not os.environ.get("TARGET_DIRECTORY")
    and settings.target_directory == original_target_directory
    and not Path(settings.target_directory).exists()
):
    # If it's the default and doesn't exist, create it or raise error
    raise SystemExit(
        f"Error: Target directory '{settings.target_directory}' does not exist. Please create it or update the configuration."
    )
