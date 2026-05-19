from threading import Event
import time
import unittest

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


class DownloadQueueTest(unittest.TestCase):
    def test_download_queue_processes_jobs_one_at_a_time(self) -> None:
        wrapper = RecordingWrapper()
        download_queue = DownloadQueue(wrapper)

        first_job = download_queue.enqueue("first")
        second_job = download_queue.enqueue("second")

        self.assertEqual(first_job.id, 1)
        self.assertEqual(second_job.id, 2)
        self.assertTrue(wrapper.first_download_started.wait(timeout=1))
        time.sleep(0.05)
        self.assertEqual(wrapper.calls, [("first", "start")])
        self.assertEqual(
            download_queue.snapshot(),
            {
                "current": {"id": 1, "type": "download", "show_hash": "first"},
                "pending": [{"id": 2, "type": "download", "show_hash": "second"}],
                "pending_count": 1,
            },
        )

        wrapper.allow_first_download_to_finish.set()
        wrapper.allow_database_refresh_to_finish.set()
        download_queue.join()

        self.assertEqual(
            download_queue.snapshot(),
            {
                "current": None,
                "pending": [],
                "pending_count": 0,
            },
        )
        self.assertEqual(
            wrapper.calls,
            [
                ("first", "start"),
                ("first", "finish"),
                ("second", "start"),
                ("second", "finish"),
            ],
        )

    def test_database_refresh_shares_queue_with_downloads(self) -> None:
        wrapper = RecordingWrapper()
        download_queue = DownloadQueue(wrapper)

        download_queue.enqueue("first")
        refresh_job = download_queue.enqueue_database_refresh()

        self.assertEqual(refresh_job.id, 2)
        self.assertTrue(wrapper.first_download_started.wait(timeout=1))
        time.sleep(0.05)
        self.assertEqual(wrapper.calls, [("first", "start")])
        self.assertEqual(
            download_queue.snapshot(),
            {
                "current": {"id": 1, "type": "download", "show_hash": "first"},
                "pending": [{"id": 2, "type": "database_refresh", "show_hash": None}],
                "pending_count": 1,
            },
        )

        wrapper.allow_first_download_to_finish.set()
        wrapper.allow_database_refresh_to_finish.set()
        download_queue.join()

        self.assertEqual(
            wrapper.calls,
            [
                ("first", "start"),
                ("first", "finish"),
                ("database_refresh", "start"),
                ("database_refresh", "finish"),
            ],
        )

    def test_database_refresh_running_state_only_tracks_active_refresh(self) -> None:
        wrapper = RecordingWrapper()
        download_queue = DownloadQueue(wrapper)

        download_queue.enqueue("first")
        download_queue.enqueue_database_refresh()

        self.assertTrue(wrapper.first_download_started.wait(timeout=1))
        self.assertFalse(download_queue.database_refresh_running())

        wrapper.allow_first_download_to_finish.set()
        self.assertTrue(wrapper.database_refresh_started.wait(timeout=1))
        self.assertTrue(download_queue.database_refresh_running())

        wrapper.allow_database_refresh_to_finish.set()
        download_queue.join()

        self.assertFalse(download_queue.database_refresh_running())

    def test_database_refresh_is_not_queued_twice(self) -> None:
        wrapper = RecordingWrapper()
        download_queue = DownloadQueue(wrapper)

        download_queue.enqueue("first")
        first_refresh_job = download_queue.enqueue_database_refresh()
        second_refresh_job = download_queue.enqueue_database_refresh()

        self.assertEqual(first_refresh_job, second_refresh_job)
        self.assertEqual(first_refresh_job.id, 2)
        self.assertTrue(wrapper.first_download_started.wait(timeout=1))
        self.assertEqual(
            download_queue.snapshot(),
            {
                "current": {"id": 1, "type": "download", "show_hash": "first"},
                "pending": [{"id": 2, "type": "database_refresh", "show_hash": None}],
                "pending_count": 1,
            },
        )

        wrapper.allow_first_download_to_finish.set()
        download_queue.join()

        self.assertEqual(
            wrapper.calls,
            [
                ("first", "start"),
                ("first", "finish"),
                ("database_refresh", "start"),
                ("database_refresh", "finish"),
            ],
        )
