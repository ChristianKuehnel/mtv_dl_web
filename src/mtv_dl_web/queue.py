import logging
from dataclasses import dataclass
from queue import Queue
from threading import Lock, Thread
from typing import Optional, Protocol, TypedDict


logger = logging.getLogger(__name__)


class DownloadRunner(Protocol):
    """Object that can run a single download."""

    def download(self, show_hash: str) -> bool: ...


class DownloadJobSnapshot(TypedDict):
    id: int
    show_hash: str


class DownloadQueueSnapshot(TypedDict):
    current: Optional[DownloadJobSnapshot]
    pending: list[DownloadJobSnapshot]
    pending_count: int


@dataclass(frozen=True)
class DownloadJob:
    """A queued download request."""

    id: int
    show_hash: str

    def snapshot(self) -> DownloadJobSnapshot:
        return {"id": self.id, "show_hash": self.show_hash}


class DownloadQueue:
    """Process download requests one at a time in the background."""

    def __init__(self, wrapper: DownloadRunner):
        self._wrapper = wrapper
        self._queue: Queue[DownloadJob] = Queue()
        self._lock = Lock()
        self._next_job_id = 1
        self._current_job: Optional[DownloadJob] = None
        self._worker = Thread(
            target=self._process_jobs,
            name="mtv-dl-download-queue",
            daemon=True,
        )
        self._worker.start()

    def enqueue(self, show_hash: str) -> DownloadJob:
        """Add a download request to the queue."""
        with self._lock:
            job = DownloadJob(id=self._next_job_id, show_hash=show_hash)
            self._next_job_id += 1

        logger.info("Queueing download job %s for hash %s", job.id, job.show_hash)
        self._queue.put(job)
        return job

    def snapshot(self) -> DownloadQueueSnapshot:
        """Return a JSON-friendly view of the current queue state."""
        with self._lock:
            current = self._current_job.snapshot() if self._current_job else None

        with self._queue.mutex:
            pending = [job.snapshot() for job in self._queue.queue]

        return {
            "current": current,
            "pending": pending,
            "pending_count": len(pending),
        }

    def join(self) -> None:
        """Block until all queued jobs have been processed."""
        self._queue.join()

    def _process_jobs(self) -> None:
        while True:
            job = self._queue.get()
            try:
                with self._lock:
                    self._current_job = job

                logger.info(
                    "Starting queued download job %s for hash %s",
                    job.id,
                    job.show_hash,
                )
                success = self._wrapper.download(job.show_hash)
                if success:
                    logger.info("Queued download job %s completed", job.id)
                else:
                    logger.error("Queued download job %s failed", job.id)
            except Exception:
                logger.exception("Queued download job %s crashed", job.id)
            finally:
                with self._lock:
                    self._current_job = None
                self._queue.task_done()
