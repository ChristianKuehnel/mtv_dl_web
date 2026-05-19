from mtv_dl_web.scheduler import DatabaseRefreshScheduler


class RecordingQueue:
    def __init__(self) -> None:
        self.refresh_count = 0

    def enqueue_database_refresh(self) -> None:
        self.refresh_count += 1


def test_database_refresh_scheduler_enqueues_refresh_job() -> None:
    queue = RecordingQueue()
    scheduler = DatabaseRefreshScheduler(
        queue,
        cron_expression="0 3 * * *",
        timezone="Europe/Berlin",
    )

    scheduler._enqueue_database_refresh()

    assert queue.refresh_count == 1


def test_database_refresh_scheduler_accepts_crontab_expression() -> None:
    queue = RecordingQueue()

    scheduler = DatabaseRefreshScheduler(
        queue,
        cron_expression="0 3 * * *",
        timezone="Europe/Berlin",
    )

    jobs = scheduler._scheduler.get_jobs()
    assert len(jobs) == 1
    assert jobs[0].id == "database_refresh"
