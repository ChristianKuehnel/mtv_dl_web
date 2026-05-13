# Story 1.8: Implement Proper Locking for All Shared Mutable State

Status: ready-for-dev

## Story

As a self-hosting user,
I want the MTV Downloader web interface to protect all shared mutable state,
so that the application remains stable and data integrity is maintained under concurrent usage (NFR-20).

## Acceptance Criteria

1. **Given** multiple shared mutable state variables, **when** multiple threads access them simultaneously, **then** all shared state is protected from race conditions and data integrity is maintained.
2. **Given** database refresh and download operations run simultaneously, **when** both access shared resources, **then** no conflicts occur and both operations complete successfully.
3. **Given** global state variables are modified by multiple threads, **when** updates happen concurrently, **then** modifications are atomic/consistent with no partial updates.

## Tasks / Subtasks

- [ ] Inventory all shared mutable state (refresh flags, queue/download maps, counters) (AC: 1)
- [ ] Define lock ownership/order policy to avoid deadlocks (AC: 1, 2, 3)
- [ ] Refactor unsafe access paths to centralized helpers with locking (AC: 1, 3)
- [ ] Add concurrent integration tests covering refresh + download + status operations (AC: 2)

## Dev Notes

- In `main.py`, shared mutable candidates include: `active_downloads`, `_database_update_count`, `is_database_refreshing`, `database_refresh_task`, `database_last_refresh_time`.
- Preserve lock granularity; do not expand locks around blocking calls to `Database`/`Downloader` operations.
- Use consistent lock ordering where multiple locks are needed to prevent deadlocks.
- Keep endpoint behavior and payloads backwards-compatible.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` Story 1.8]
- [Source: `_bmad-output/planning-artifacts/prd.md` NFR-20]
- [Source: `src/mtv_dl_web/main.py` threading and refresh sections]

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
