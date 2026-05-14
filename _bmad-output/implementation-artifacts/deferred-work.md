## Deferred from: code review of 1-9-concurrency-improvements.md (2026-05-13)

- Exception cleanup test may not mutate shared module state due to local variable shadowing (`tests/test_concurrent_access_stress.py:198`).
- Lock-order invariant is documented, but opposite lock-acquisition/deadlock path is not evidenced as tested (`tests/test_concurrent_access_stress.py:154`).

## Deferred from: code review of 1-8-implement-proper-locking.md (2026-05-13)

- Establish and document a global lock acquisition order for shared-state locks (e.g., `download_queue_lock` and `active_downloads_lock`) to reduce future deadlock risk as multi-lock paths are added.

## Deferred from: code review of 1-13-implement-download-naming-patterns.md (2026-05-14)

- Returned download path not resolved to absolute [src/mtv_dl_web/main.py:545] — pre-existing, returned path from mtv_dl.download() stored as str(path) without .resolve() or .absolute()
- Symlink-unresolved target path enables undetected escape [src/mtv_dl_web/main.py:467] — pre-existing, Path.expanduser() without .resolve() enables symlink-based path escape
- Empty quality string not rejected [src/mtv_dl_web/main.py:81] — pre-existing, DownloadRequest.quality str type with no validation, empty string silently falls to default

## Deferred from: code review of 1-13-implement-download-naming-patterns.md (2026-05-14)

- Returned download path not resolved to absolute [src/mtv_dl_web/main.py:546] — pre-existing, status stores mtv_dl return path without canonical absolute normalization.
- Symlink-unresolved target path enables undetected escape [src/mtv_dl_web/main.py:467] — pre-existing, target directory path is expanded but not resolved before downstream containment assumptions.
- Empty/variant quality values still silently fall back [src/mtv_dl_web/main.py:81] — pre-existing, quality input lacks normalization/validation for empty/whitespace/case variants.
