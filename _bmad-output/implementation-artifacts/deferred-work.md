## Deferred from: code review of 1-8-implement-proper-locking.md (2026-05-13)

- Establish and document a global lock acquisition order for shared-state locks (e.g., `download_queue_lock` and `active_downloads_lock`) to reduce future deadlock risk as multi-lock paths are added.
