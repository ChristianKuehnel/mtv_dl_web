# Story 1.10: Improve Database Refresh Cadence, Status, and Logging

Status: done

## Story

As a self-hosting user,
I want database refreshes to run on an explicit cadence with clear UI status and logs,
so that searches use fresh data without blocking normal app usage or hiding refresh failures.

## Acceptance Criteria

1. **Given** default configuration, **when** the service starts, **then** database refresh is scheduled once every 24 hours unless overridden (FR-34).
2. **Given** user-provided refresh schedule config, **when** startup validation runs, **then** APScheduler `CronTrigger.from_crontab()` five-field syntax is accepted.
3. **Given** unsupported cron syntax, **when** startup validation runs, **then** configuration is rejected before scheduling with clear validation logs (NFR-7).
4. **Given** a user performs search/download, **when** no manual/scheduled refresh is active, **then** those operations do not implicitly trigger refresh (FR-35).
5. **Given** refresh success, **when** UI/status API is queried, **then** last successful update time and database age are exposed when available (FR-36).
6. **Given** refresh lifecycle events, **when** logs are inspected, **then** trigger source, outcome, and duration are recorded (FR-37).

## Tasks / Subtasks

- [x] Add explicit refresh scheduler with default 24h cadence (AC: 1)
- [x] Validate refresh cron with APScheduler five-field crontab syntax (AC: 2, 3)
- [x] Separate refresh triggers from search/download request paths (AC: 4)
- [x] Expose refresh metadata for UI and status API (AC: 5)
- [x] Implement structured logging for refresh start/success/failure/duration/source (AC: 6)
- [x] Add tests for schedule validation, trigger boundaries, and status/log behavior (AC: 1-6)

### Review Findings

- [x] [Review][Patch] Scheduler only initializes under `__main__`, so periodic refresh may never start in ASGI deployments [src/mtv_dl_web/main.py:718]
- [x] [Review][Patch] Refresh in-progress state is not set before scheduling, allowing duplicate manual refresh triggers and incorrect `is_refreshing` status [src/mtv_dl_web/main.py:700]
- [x] [Review][Patch] `last_refresh_time` is returned by status API but never updated after refresh completion [src/mtv_dl_web/main.py:384]
- [x] [Review][Patch] Refresh lifecycle logs do not record true trigger source (manual vs scheduled) [src/mtv_dl_web/main.py:371]
- [x] [Review][Patch] Status endpoint adds blocking DB construction in async path, risking event-loop stalls [src/mtv_dl_web/main.py:425]
- [x] [Review][Patch] Manual refresh uses `GET` for state-changing behavior, which is unsafe/idempotency-breaking [src/mtv_dl_web/main.py:700]
- [x] [Review][Patch] Duplicate refresh global declarations and non-global schedule assignment risk inconsistent runtime state [src/mtv_dl_web/main.py:68]

## Dev Notes

- Current implementation in `main.py` opportunistically triggers refresh from request flow (`get_db_connection`); Story 1.10 must remove this implicit trigger pattern for search/download.
- Keep Story 1.6 responsiveness: refresh work remains non-blocking to API/UI.
- Align all scheduler semantics with PRD/APScheduler requirement: `minute hour day_of_month month day_of_week` only.
- Ensure status API exposes timestamp/age safely even when mtv_dl internals are unavailable.

### File Structure Requirements

- `src/mtv_dl_web/main.py` (refresh trigger/scheduler/status/logging updates)
- Optional supporting module(s) under `src/mtv_dl_web/` if needed
- `tests/` for validation, status, and logging behavior

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` Story 1.10]
- [Source: `_bmad-output/planning-artifacts/prd.md` FR-34, FR-35, FR-36, FR-37, NFR-7]
- [Source: `_bmad-output/project-context.md` Development workflow rules]

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Completion Notes List

- Implemented explicit database refresh scheduler with default 24h cadence
- Added cron validation with APScheduler five-field syntax validation
- Separated refresh triggers from search/download request paths
- Exposed refresh metadata for UI and status API
- Implemented structured logging for refresh lifecycle events
- Created test suite for validation of new functionality
