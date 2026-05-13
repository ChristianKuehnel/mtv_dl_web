#!/usr/bin/env python3

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import mtv_dl_web.main as main


def test_sanitize_filename_component_replaces_spaces_and_special_chars() -> None:
    sanitized = main.sanitize_filename_component("A Show: Episode/One?")
    assert sanitized == "A_Show_Episode_One"


def test_generate_download_filename_for_series_content() -> None:
    show = {"title": "Episode One", "topic": "Great Series", "season": 1, "episode": 2}
    filename = main.generate_download_filename(show, ".mp4")
    assert filename == "Great_Series_-_Episode_One.mp4"


def test_generate_download_filename_for_non_series_content() -> None:
    show = {"title": "Standalone Film", "topic": "Standalone Film", "season": None, "episode": None}
    filename = main.generate_download_filename(show, ".ts")
    assert filename == "Standalone_Film.ts"


def test_validate_download_path_accepts_target_directory_and_pattern(tmp_path: Path) -> None:
    target_dir = tmp_path / "downloads"
    target_dir.mkdir()
    file_path = target_dir / "Great_Series_-_Episode_One.mp4"
    file_path.write_text("x", encoding="utf-8")

    show = {"title": "Episode One", "topic": "Great Series", "season": 1, "episode": 2}
    is_valid = main.validate_download_naming(file_path, target_dir, show)
    assert is_valid is True


def test_validate_download_path_rejects_file_outside_target(tmp_path: Path) -> None:
    target_dir = tmp_path / "downloads"
    target_dir.mkdir()
    outside_file = tmp_path / "Great_Series_-_Episode_One.mp4"
    outside_file.write_text("x", encoding="utf-8")

    show = {"title": "Episode One", "topic": "Great Series", "season": 1, "episode": 2}
    is_valid = main.validate_download_naming(outside_file, target_dir, show)
    assert is_valid is False


def test_download_background_sets_validated_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    target_dir = tmp_path / "downloads"
    target_dir.mkdir()
    source_file = tmp_path / "source.mp4"
    source_file.write_text("video", encoding="utf-8")

    show = {"hash": "abc123", "title": "Episode One", "topic": "Great Series", "season": 1, "episode": 2}
    request = main.DownloadRequest(filters=["channel=ARD"], target_directory=str(target_dir))

    class FakeDownloader:
        def __init__(self, _show_data):
            pass

        def download(self, **_kwargs):
            return source_file

    monkeypatch.setattr(main, "Downloader", FakeDownloader)
    main.active_downloads["abc123"] = {"status": "queued", "progress": 0.0, "message": "Queued", "file_path": None}

    import asyncio

    asyncio.run(main.download_show_background(show, request))

    status = main.active_downloads["abc123"]
    assert status["status"] == "completed"
    assert status["file_path"] is not None
    assert Path(status["file_path"]).parent == target_dir
