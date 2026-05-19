"""Schedule recurring background work."""

from __future__ import annotations

import logging
from typing import Protocol

from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore[import-untyped]
from apscheduler.triggers.cron import CronTrigger  # type: ignore[import-untyped]


class RefreshQueue(Protocol):
    def enqueue_database_refresh(self) -> object: ...


logger = logging.getLogger(__name__)


class DatabaseRefreshScheduler:
    """Enqueue database refresh jobs from a cron schedule."""

    def __init__(
        self,
        queue: RefreshQueue,
        cron_expression: str,
        timezone: str,
    ):
        self._queue = queue
        self._scheduler = BackgroundScheduler(timezone=timezone)
        trigger = CronTrigger.from_crontab(cron_expression, timezone=timezone)
        self._scheduler.add_job(
            self._enqueue_database_refresh,
            trigger=trigger,
            id="database_refresh",
            coalesce=True,
            max_instances=1,
        )

    def start(self) -> None:
        logger.info("Starting database refresh scheduler")
        self._scheduler.start()

    def stop(self) -> None:
        self._scheduler.shutdown(wait=False)

    def _enqueue_database_refresh(self) -> None:
        logger.info("Queueing scheduled database refresh")
        self._queue.enqueue_database_refresh()
