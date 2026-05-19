from threading import Event
import time
import unittest

from mtv_dl_web.queue import DownloadQueue


class RecordingWrapper:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []
        self.first_download_started = Event()
        self.allow_first_download_to_finish = Event()

    def download(self, show_hash: str) -> bool:
        self.calls.append((show_hash, "start"))
        if show_hash == "first":
            self.first_download_started.set()
            self.allow_first_download_to_finish.wait(timeout=1)
        self.calls.append((show_hash, "finish"))
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
                "current": {"id": 1, "show_hash": "first"},
                "pending": [{"id": 2, "show_hash": "second"}],
                "pending_count": 1,
            },
        )

        wrapper.allow_first_download_to_finish.set()
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
