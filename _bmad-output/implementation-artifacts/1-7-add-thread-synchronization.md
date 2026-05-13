# Story 1.7: Add Thread Synchronization to active_downloads Dictionary Access

Status: ready-for-dev

## Story

As a self-hosting user,
I want the MTV Downloader web interface to protect active download status updates,
so that concurrent requests and background work do not cause race conditions or data corruption (NFR-20).

## Acceptance Criteria

1. **Given** multiple background download tasks run simultaneously, **when** they update download status concurrently, **then** the application does not crash or corrupt data and all statuses are recorded.
2. **Given** active downloads and concurrent status viewers, **when** requests and background updates happen together, **then** status queries remain consistent and race-free.
3. **Given** active downloads during graceful shutdown, **when** the app stops, **then** active download state is safely managed without corruption.

## Tasks / Subtasks

- [ ] Audit all read/write access paths to `active_downloads` (AC: 1, 2, 3)
- [ ] Enforce consistent lock usage for all mutations and reads (AC: 1, 2)
- [ ] Add shutdown-safe handling for in-flight background tasks and status map finalization (AC: 3)
- [ ] Add deterministic concurrency tests and failure-path coverage (AC: 1, 2, 3)

## Dev Notes

- Existing `active_downloads_lock = threading.RLock()` is present; ensure no unlocked access remains (including delete/status paths).
- Avoid long lock hold times around network or disk operations; lock only around shared state reads/writes.
- Keep current download API contracts and response payload fields unchanged.
- Preserve Story 1.6 non-blocking refresh behavior while tightening shared-state safety.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` Story 1.7]
- [Source: `_bmad-output/planning-artifacts/prd.md` NFR-20]
- [Source: `src/mtv_dl_web/main.py` shared state and download endpoints]

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
