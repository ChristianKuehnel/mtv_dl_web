#!/usr/bin/env python3

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

if "mtv_dl" not in sys.modules:
    mtv_dl_module = types.ModuleType("mtv_dl")
    mtv_dl_submodule = types.ModuleType("mtv_dl.mtv_dl")
    mtv_dl_submodule.Database = object
    mtv_dl_submodule.Downloader = object
    mtv_dl_module.mtv_dl = mtv_dl_submodule
    sys.modules["mtv_dl"] = mtv_dl_module
    sys.modules["mtv_dl.mtv_dl"] = mtv_dl_submodule

import mtv_dl_web.main as main
from mtv_dl_web.main import app

client = TestClient(app)


class FakeDb:
    def __init__(self, rows: list[dict[str, object]]):
        self.filtered = MagicMock(return_value=rows)


@pytest.fixture
def no_background_download(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _noop_download(*args: object, **kwargs: object) -> None:
        return None

    monkeypatch.setattr(main, "download_show_background", _noop_download)


@pytest.fixture
def clear_active_downloads() -> None:
    with main.active_downloads_lock:
        main.active_downloads.clear()


def _mock_db(monkeypatch: pytest.MonkeyPatch, rows: list[dict[str, object]]) -> None:
    fake_db = FakeDb(rows)
    monkeypatch.setattr(main, "get_db_connection", lambda *args, **kwargs: fake_db)


def _show(show_hash: str, title: str) -> dict[str, object]:
    return {
        "hash": show_hash,
        "channel": "ARD",
        "title": title,
        "topic": "News",
        "size": 100,
        "start": "2023-01-01T12:00:00",
        "duration": "30m",
        "age": "7d",
        "region": "DE",
        "downloaded": None,
    }


def test_download_selected_one_item_only(monkeypatch: pytest.MonkeyPatch, no_background_download: None, clear_active_downloads: None) -> None:
    rows = [_show("a1", "First"), _show("b2", "Second")]
    _mock_db(monkeypatch, rows)

    response = client.post(
        "/api/download",
        json={
            "filters": ["channel=ARD"],
            "selected_hashes": ["b2"],
            "quality": "medium",
            "target_directory": "./downloads",
            "include_subtitles": True,
            "include_nfo": True,
            "merge_to_mkv": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["download_ids"] == ["b2"]
    with main.active_downloads_lock:
        assert set(main.active_downloads.keys()) == {"b2"}


def test_download_selected_multiple_items_once(monkeypatch: pytest.MonkeyPatch, no_background_download: None, clear_active_downloads: None) -> None:
    rows = [_show("a1", "First"), _show("b2", "Second"), _show("c3", "Third")]
    _mock_db(monkeypatch, rows)

    response = client.post(
        "/api/download",
        json={
            "filters": ["channel=ARD"],
            "selected_hashes": ["c3", "a1", "a1"],
            "quality": "medium",
            "target_directory": "./downloads",
            "include_subtitles": True,
            "include_nfo": True,
            "merge_to_mkv": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["download_ids"] == ["c3", "a1"]
    with main.active_downloads_lock:
        assert set(main.active_downloads.keys()) == {"a1", "c3"}


def test_download_selected_unknown_or_empty_rejected(monkeypatch: pytest.MonkeyPatch, no_background_download: None, clear_active_downloads: None) -> None:
    rows = [_show("a1", "First")]
    _mock_db(monkeypatch, rows)

    empty_selection = client.post(
        "/api/download",
        json={
            "filters": ["channel=ARD"],
            "selected_hashes": [],
            "target_directory": "./downloads",
        },
    )
    assert empty_selection.status_code == 400

    unknown_selection = client.post(
        "/api/download",
        json={
            "filters": ["channel=ARD"],
            "selected_hashes": ["missing"],
            "target_directory": "./downloads",
        },
    )
    assert unknown_selection.status_code == 404
    with main.active_downloads_lock:
        assert main.active_downloads == {}


@pytest.mark.asyncio
async def test_download_background_marks_completed_for_in_target_path(monkeypatch: pytest.MonkeyPatch, clear_active_downloads: None) -> None:
    class FakeDownloader:
        def __init__(self, _show_data: dict[str, object]) -> None:
            pass

        def download(self, **kwargs: object) -> str:
            target = kwargs["target"]
            return str(target / "nested" / "episode.mp4")

    monkeypatch.setattr(main, "Downloader", FakeDownloader)

    show_id = "inside-target"
    with main.active_downloads_lock:
        main.active_downloads[show_id] = {"status": "queued", "progress": 0.0, "message": "Queued", "file_path": None}

    await main.download_show_background({"hash": show_id}, main.DownloadRequest(filters=["channel=ARD"], selected_hashes=[show_id]),
                                       Path("/downloads"))

    with main.active_downloads_lock:
        assert main.active_downloads[show_id]["status"] == "completed"
        assert main.active_downloads[show_id]["file_path"] is not None


@pytest.mark.asyncio
async def test_download_background_marks_failed_for_outside_target_path(monkeypatch: pytest.MonkeyPatch, clear_active_downloads: None) -> None:
    class FakeDownloader:
        def __init__(self, _show_data: dict[str, object]) -> None:
            pass

        def download(self, **kwargs: object) -> str:
            return "/tmp/episode.mp4"

    monkeypatch.setattr(main, "Downloader", FakeDownloader)

    show_id = "outside-target"
    with main.active_downloads_lock:
        main.active_downloads[show_id] = {"status": "queued", "progress": 0.0, "message": "Queued", "file_path": None}

    await main.download_show_background({"hash": show_id}, main.DownloadRequest(filters=["channel=ARD"], selected_hashes=[show_id]),
                                       Path("/downloads"))

    with main.active_downloads_lock:
        assert main.active_downloads[show_id]["status"] == "failed"
        assert "outside target directory" in main.active_downloads[show_id]["message"]


@pytest.mark.asyncio
async def test_download_background_marks_failed_for_missing_path(monkeypatch: pytest.MonkeyPatch, clear_active_downloads: None) -> None:
    class FakeDownloader:
        def __init__(self, _show_data: dict[str, object]) -> None:
            pass

        def download(self, **kwargs: object) -> None:
            return None

    monkeypatch.setattr(main, "Downloader", FakeDownloader)

    show_id = "missing-path"
    with main.active_downloads_lock:
        main.active_downloads[show_id] = {"status": "queued", "progress": 0.0, "message": "Queued", "file_path": None}

    await main.download_show_background({"hash": show_id}, main.DownloadRequest(filters=["channel=ARD"], selected_hashes=[show_id]),
                                       Path("/downloads"))

    with main.active_downloads_lock:
        assert main.active_downloads[show_id]["status"] == "failed"
