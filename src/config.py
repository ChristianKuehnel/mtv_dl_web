# Basic Configuration for MTV Downloader Web

import os

from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    # Service configuration
    port: int = 8000
    host: str = "0.0.0.0"

    # Database configuration
    database_path: str = os.path.expanduser("~/.mtv_dl_web/filmliste.sqlite")

    # Download configuration
    download_quality: str = "best"
    target_directory: str = os.path.expanduser("~/Downloads/mtv_dl")

    # Feature flags
    enable_subtitles: bool = False
    enable_nfo: bool = False
    enable_mkv_merge: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
