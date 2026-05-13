# Story 1.6: Enable Concurrent Web UI Access During Database Refresh

Status: done

## Story

As a self-hosting user,
I want to access the web UI and perform status/queue operations while the database is refreshing,
so that I can monitor the system and manage downloads without interruption.

## Acceptance Criteria

1. **Given** a database refresh operation is in progress, **when** I access the web UI, **then** the UI remains accessible and shows current status and download queue (NFR-18, AC-19).
2. **Given** a database refresh operation is in progress, **when** I make health check or status API requests, **then** they complete successfully within performance targets (NFR-19, AC-20).
3. **Given** a database refresh operation is in progress, **when** I perform queue management operations (view, add, remove items), **then** they execute normally without being blocked by the refresh operation (NFR-19, AC-21).
4. **Given** concurrent database refresh and user operations, **when** both are executing, **then** the system maintains data consistency and operational integrity.

## Tasks / Subtasks

- [ ] Ensure refresh execution is non-blocking to request handlers (AC: 1, 2, 3)
  - [ ] Keep refresh scheduling in background execution path
  - [ ] Prevent duplicate overlapping refresh jobs and stale flags
- [ ] Keep health/status endpoints responsive during refresh (AC: 2)
  - [ ] Return `updating` when refresh is in progress
  - [ ] Maintain latency target behavior under load
- [ ] Preserve queue operation behavior during refresh (AC: 3)
  - [ ] Verify add/view/remove paths remain available during refresh
  - [ ] Protect shared mutable state with locks where required
- [ ] Add concurrency tests (AC: 1, 2, 3, 4)
  - [ ] API responsiveness under active refresh
  - [ ] Queue safety and consistency under concurrent operations

## Dev Notes

### Current State To Preserve

- `main.py` already has refresh state globals (`is_database_refreshing`, `database_refresh_task`, locks) and health-state wiring.
- Frontend (`index.html`) polls `/health` and maps `healthy/updating/unhealthy` to `online/updating/offline`.
- Download/queue state uses in-memory `active_downloads` with `RLock`.

### Required Implementation Guardrails

- Do not regress Story 1.5 health indicator semantics.
- Do not block request handlers with synchronous `update_if_old()` during normal API flow.
- Keep all shared state mutation lock-protected to satisfy NFR-20 trajectory in Stories 1.7-1.9.

### File Structure Requirements

- Backend: `src/mtv_dl_web/main.py`.
- Frontend status wiring: `src/mtv_dl_web/frontend/index.html` (only if behavior changes).
- Tests: `tests/test_concurrent_database_access.py` and related endpoint tests.

### Testing Requirements

- Verify p95 latency/timeout guard around health/status requests during refresh.
- Verify queue operations (including remove) succeed during active refresh.
- Add race-condition-focused tests for refresh flag/state integrity.

### Previous Story Intelligence

- Story 1.5 patches identified stale health polling and weak latency assertions; keep timeout and percentile-aware checks.
- Recent reviews found disconnected refresh flags can misreport state; keep a single source of truth for refresh status.

### Git Intelligence Summary

- Recent commits repeatedly fixed concurrency/reporting edge cases; prioritize deterministic locking and explicit tests over ad hoc state toggles.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` Story 1.6]
- [Source: `_bmad-output/planning-artifacts/prd.md` NFR-18, NFR-19, AC-19, AC-20, AC-21]
- [Source: `_bmad-output/project-context.md` Async pattern, Testing rules]

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- To be filled during implementation.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.

### File List

- `src/mtv_dl_web/main.py` (update)
- `src/mtv_dl_web/frontend/index.html` (possible update)
- `tests/...` (new/updated)
