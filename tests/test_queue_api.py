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
def clear_active_downloads() -> None:
    with main.active_downloads_lock:
        main.active_downloads.clear()


def _show(show_hash: str) -> dict[str, object]:
    return {
        "hash": show_hash,
        "channel": "ARD",
        "title": "Item",
        "topic": "News",
        "size": 100,
        "start": "2023-01-01T12:00:00",
        "duration": "30m",
        "age": "7d",
        "region": "DE",
        "downloaded": None,
    }


def test_queue_add_list_remove_pending(monkeypatch: pytest.MonkeyPatch, clear_active_downloads: None) -> None:
    monkeypatch.setattr(main, "get_db_connection", lambda *args, **kwargs: FakeDb([_show("abc123")]))
    monkeypatch.setattr(main, "_promote_next_pending_download", lambda: None)

    add_response = client.post("/queue", json={"video_id": "abc123"})
    assert add_response.status_code == 200

    list_response = client.get("/queue")
    assert list_response.status_code == 200
    queue_items = list_response.json()["items"]
    assert len(queue_items) == 1
    assert queue_items[0]["id"] == "abc123"
    assert queue_items[0]["status"] == "pending"

    remove_response = client.delete("/queue/abc123")
    assert remove_response.status_code == 200


def test_queue_rejects_unknown_or_malformed_requests(
    monkeypatch: pytest.MonkeyPatch, clear_active_downloads: None
) -> None:
    monkeypatch.setattr(main, "get_db_connection", lambda *args, **kwargs: FakeDb([]))

    bad_payload = client.post("/queue", json={"video_id": ""})
    assert bad_payload.status_code == 400

    unknown_id = client.post("/queue", json={"video_id": "missing"})
    assert unknown_id.status_code == 404


def test_queue_prevents_removing_non_pending(monkeypatch: pytest.MonkeyPatch, clear_active_downloads: None) -> None:
    monkeypatch.setattr(main, "get_db_connection", lambda *args, **kwargs: FakeDb([_show("abc123")]))

    with main.active_downloads_lock:
        main.active_downloads["abc123"] = {
            "status": "downloading",
            "progress": 0.1,
            "message": "Starting download...",
            "file_path": None,
            "show_data": _show("abc123"),
            "request_payload": main.DownloadRequest(filters=["hash=abc123"], selected_hashes=["abc123"]).model_dump(),
        }

    response = client.delete("/queue/abc123")
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_single_active_promotion_after_failure(
    monkeypatch: pytest.MonkeyPatch, clear_active_downloads: None
) -> None:
    class FailingDownloader:
        def __init__(self, _show_data: dict[str, object]) -> None:
            pass

        def download(self, **kwargs: object) -> str:
            raise RuntimeError("boom")

    monkeypatch.setattr(main, "Downloader", FailingDownloader)
    promoted: list[str] = []

    def fake_promote() -> None:
        with main.active_downloads_lock:
            pending = [k for k, v in main.active_downloads.items() if v["status"] == "pending"]
            if pending:
                main.active_downloads[pending[0]]["status"] = "downloading"
                promoted.append(pending[0])

    monkeypatch.setattr(main, "_promote_next_pending_download", fake_promote)

    with main.active_downloads_lock:
        main.active_downloads["first"] = {
            "status": "downloading",
            "progress": 0.0,
            "message": "Starting",
            "file_path": None,
            "show_data": _show("first"),
            "request_payload": main.DownloadRequest(filters=["hash=first"], selected_hashes=["first"]).model_dump(),
        }
        main.active_downloads["second"] = {
            "status": "pending",
            "progress": 0.0,
            "message": "Queued",
            "file_path": None,
            "show_data": _show("second"),
            "request_payload": main.DownloadRequest(filters=["hash=second"], selected_hashes=["second"]).model_dump(),
        }

    await main.download_show_background(
        {"hash": "first"},
        main.DownloadRequest(filters=["hash=first"], selected_hashes=["first"]),
        Path("/downloads"),
    )

    with main.active_downloads_lock:
        assert main.active_downloads["first"]["status"] == "failed"
    assert "second" in promoted
