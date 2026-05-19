from threading import Event
import time

import pytest

from mtv_dl_web.queue import DownloadQueue


class RecordingWrapper:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []
        self.first_download_started = Event()
        self.allow_first_download_to_finish = Event()
        self.database_refresh_started = Event()
        self.allow_database_refresh_to_finish = Event()

    def download(self, show_hash: str) -> bool:
        self.calls.append((show_hash, "start"))
        if show_hash == "first":
            self.first_download_started.set()
            self.allow_first_download_to_finish.wait(timeout=1)
        self.calls.append((show_hash, "finish"))
        return True

    def refresh_database(self) -> bool:
        self.calls.append(("database_refresh", "start"))
        self.database_refresh_started.set()
        self.allow_database_refresh_to_finish.wait(timeout=1)
        self.calls.append(("database_refresh", "finish"))
        return True


@pytest.fixture
def wrapper() -> RecordingWrapper:
    return RecordingWrapper()


@pytest.fixture
def download_queue(wrapper: RecordingWrapper) -> DownloadQueue:
    return DownloadQueue(wrapper)


def test_download_queue_processes_jobs_one_at_a_time(
    wrapper: RecordingWrapper, download_queue: DownloadQueue
) -> None:
    first_job = download_queue.enqueue("first", "First Show")
    second_job = download_queue.enqueue("second")

    assert first_job.id == 1
    assert second_job.id == 2
    assert wrapper.first_download_started.wait(timeout=1)
    time.sleep(0.05)
    assert wrapper.calls == [("first", "start")]
    assert download_queue.snapshot() == {
        "current": {
            "id": 1,
            "type": "download",
            "show_hash": "first",
            "title": "First Show",
        },
        "pending": [
            {"id": 2, "type": "download", "show_hash": "second", "title": None}
        ],
        "pending_count": 1,
    }

    wrapper.allow_first_download_to_finish.set()
    wrapper.allow_database_refresh_to_finish.set()
    download_queue.join()

    assert download_queue.snapshot() == {
        "current": None,
        "pending": [],
        "pending_count": 0,
    }
    assert wrapper.calls == [
        ("first", "start"),
        ("first", "finish"),
        ("second", "start"),
        ("second", "finish"),
    ]


def test_database_refresh_shares_queue_with_downloads(
    wrapper: RecordingWrapper, download_queue: DownloadQueue
) -> None:
    download_queue.enqueue("first")
    refresh_job = download_queue.enqueue_database_refresh()

    assert refresh_job.id == 2
    assert wrapper.first_download_started.wait(timeout=1)
    time.sleep(0.05)
    assert wrapper.calls == [("first", "start")]
    assert download_queue.snapshot() == {
        "current": {
            "id": 1,
            "type": "download",
            "show_hash": "first",
            "title": None,
        },
        "pending": [
            {
                "id": 2,
                "type": "database_refresh",
                "show_hash": None,
                "title": None,
            }
        ],
        "pending_count": 1,
    }

    wrapper.allow_first_download_to_finish.set()
    wrapper.allow_database_refresh_to_finish.set()
    download_queue.join()

    assert wrapper.calls == [
        ("first", "start"),
        ("first", "finish"),
        ("database_refresh", "start"),
        ("database_refresh", "finish"),
    ]


def test_database_refresh_running_state_only_tracks_active_refresh(
    wrapper: RecordingWrapper, download_queue: DownloadQueue
) -> None:
    download_queue.enqueue("first")
    download_queue.enqueue_database_refresh()

    assert wrapper.first_download_started.wait(timeout=1)
    assert not download_queue.database_refresh_running()

    wrapper.allow_first_download_to_finish.set()
    assert wrapper.database_refresh_started.wait(timeout=1)
    assert download_queue.database_refresh_running()

    wrapper.allow_database_refresh_to_finish.set()
    download_queue.join()

    assert not download_queue.database_refresh_running()


def test_database_refresh_is_not_queued_twice(
    wrapper: RecordingWrapper, download_queue: DownloadQueue
) -> None:
    download_queue.enqueue("first")
    first_refresh_job = download_queue.enqueue_database_refresh()
    second_refresh_job = download_queue.enqueue_database_refresh()

    assert first_refresh_job == second_refresh_job
    assert first_refresh_job.id == 2
    assert wrapper.first_download_started.wait(timeout=1)
    assert download_queue.snapshot() == {
        "current": {
            "id": 1,
            "type": "download",
            "show_hash": "first",
            "title": None,
        },
        "pending": [
            {
                "id": 2,
                "type": "database_refresh",
                "show_hash": None,
                "title": None,
            }
        ],
        "pending_count": 1,
    }

    wrapper.allow_first_download_to_finish.set()
    wrapper.allow_database_refresh_to_finish.set()
    download_queue.join()

    assert wrapper.calls == [
        ("first", "start"),
        ("first", "finish"),
        ("database_refresh", "start"),
        ("database_refresh", "finish"),
    ]
