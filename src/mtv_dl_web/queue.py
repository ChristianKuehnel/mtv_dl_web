import logging
from dataclasses import dataclass
from queue import Queue
from threading import Lock, Thread
from typing import Literal, Optional, Protocol, TypedDict


logger = logging.getLogger(__name__)


class WorkRunner(Protocol):
    """Object that can run queued background work."""

    def download(self, show_hash: str) -> bool: ...

    def refresh_database(self) -> bool: ...


JobKind = Literal["download", "database_refresh"]


class WorkJobSnapshot(TypedDict):
    id: int
    type: JobKind
    show_hash: Optional[str]
    title: Optional[str]


class WorkQueueSnapshot(TypedDict):
    current: Optional[WorkJobSnapshot]
    pending: list[WorkJobSnapshot]
    pending_count: int


@dataclass(frozen=True)
class WorkJob:
    """A queued background work request."""

    id: int
    type: JobKind
    show_hash: Optional[str] = None
    title: Optional[str] = None

    def snapshot(self) -> WorkJobSnapshot:
        return {
            "id": self.id,
            "type": self.type,
            "show_hash": self.show_hash,
            "title": self.title,
        }


class DownloadQueue:
    """Process download and database refresh requests one at a time."""

    def __init__(self, wrapper: WorkRunner):
        self._wrapper = wrapper
        self._queue: Queue[WorkJob] = Queue()
        self._lock = Lock()
        self._next_job_id = 1
        self._current_job: Optional[WorkJob] = None
        self._database_refresh_in_queue = False
        self._database_refresh_job: Optional[WorkJob] = None
        self._worker = Thread(
            target=self._process_jobs,
            name="mtv-dl-work-queue",
            daemon=True,
        )
        self._worker.start()

    def enqueue(self, show_hash: str, title: Optional[str] = None) -> WorkJob:
        """Add a download request to the queue."""
        with self._lock:
            job = WorkJob(
                id=self._next_job_id,
                type="download",
                show_hash=show_hash,
                title=title,
            )
            self._next_job_id += 1

        logger.info("Queueing download job %s for hash %s", job.id, job.show_hash)
        self._queue.put(job)
        return job

    def enqueue_database_refresh(self) -> WorkJob:
        """Add a database refresh request unless one is already queued or running."""
        with self._lock:
            if self._database_refresh_in_queue:
                if self._database_refresh_job is None:
                    raise RuntimeError("Database refresh is already running")
                return self._database_refresh_job

            job = WorkJob(id=self._next_job_id, type="database_refresh")
            self._next_job_id += 1
            self._database_refresh_in_queue = True
            self._database_refresh_job = job
            self._queue.put(job)

        logger.info("Queueing database refresh job %s", job.id)
        return job

    def snapshot(self) -> WorkQueueSnapshot:
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

    def database_refresh_running(self) -> bool:
        """Return whether a database refresh is currently running."""
        with self._lock:
            return (
                self._current_job is not None
                and self._current_job.type == "database_refresh"
            )

    def join(self) -> None:
        """Block until all queued jobs have been processed."""
        self._queue.join()

    def _process_jobs(self) -> None:
        while True:
            job = self._queue.get()
            try:
                with self._lock:
                    self._current_job = job

                success = self._run_job(job)
                if success:
                    logger.info("Queued %s job %s completed", job.type, job.id)
                else:
                    logger.error("Queued %s job %s failed", job.type, job.id)
            except Exception:
                logger.exception("Queued %s job %s crashed", job.type, job.id)
            finally:
                with self._lock:
                    self._current_job = None
                    if job.type == "database_refresh":
                        self._database_refresh_in_queue = False
                        self._database_refresh_job = None
                self._queue.task_done()

    def _run_job(self, job: WorkJob) -> bool:
        if job.type == "database_refresh":
            logger.info("Starting queued database refresh job %s", job.id)
            return self._wrapper.refresh_database()

        if job.show_hash is None:
            raise RuntimeError("Download job is missing show hash")

        logger.info(
            "Starting queued download job %s for hash %s",
            job.id,
            job.show_hash,
        )
        return self._wrapper.download(job.show_hash)
