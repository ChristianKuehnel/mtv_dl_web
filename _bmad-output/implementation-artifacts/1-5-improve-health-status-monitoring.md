# Story 1.5: Improve Health Status Monitoring

Status: review

## Story

As a self-hosting user,
I want the Web UI to show accurate health status with three states (online/updating/offline),
So that I can quickly understand the backend status and database update state.

## Acceptance Criteria

1. **Given** a healthy backend not updating database, **when** I view the Web UI health status indicator, **then** it shows "online" with a green dot (NFR-16, AC-15).
2. **Given** a backend that is refreshing the database, **when** I view the Web UI health status indicator, **then** it shows "updating" with a yellow dot (NFR-16, AC-16).
3. **Given** an unhealthy or down backend, **when** I view the Web UI health status indicator, **then** it shows "offline" with a red dot (NFR-16, AC-17).
4. **Given** a health check request, **when** executed, **then** it completes within 1 second for 95th percentile (NFR-17, AC-18).

## Tasks / Subtasks

- [x] Add backend database-refresh status tracking (AC: 2, 4)
  - [x] Track when `Database.update_if_old()` is running
  - [x] Reset tracking state after refresh success or failure
  - [x] Keep `/health` non-blocking and under the 1 second threshold
- [x] Extend `/health` status response for UI monitoring (AC: 1, 2, 3, 4)
  - [x] Return `healthy` when service is available and no database refresh is active
  - [x] Return `updating` while database refresh is active
  - [x] Return `unhealthy` when health checks fail
- [x] Add Web UI health indicator (AC: 1, 2, 3)
  - [x] Render indicator in the first viewport
  - [x] Map healthy backend state to `online` with a green dot
  - [x] Map updating backend state to `updating` with a yellow dot
  - [x] Map unhealthy or failed health requests to `offline` with a red dot
  - [x] Poll `/health` periodically
- [x] Add Story 1.5 tests (AC: 1, 2, 3, 4)
  - [x] Cover healthy backend status
  - [x] Cover updating backend status
  - [x] Cover health-check performance threshold
  - [x] Cover UI indicator wiring and three-state labels/colors

## Dev Notes

### Project Structure Notes

- Backend: `src/mtv_dl_web/main.py`
- Frontend: `src/mtv_dl_web/frontend/index.html`
- Tests: `tests/`
- Preserve `GET /health` response shape as a single `status` field for compatibility with Story 1.2 tests.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.5]
- [Source: _bmad-output/project-context.md#Framework-Specific-Rules-FastAPI]
- [Source: _bmad-output/project-context.md#Testing-Rules]

## Dev Agent Record

### Agent Model Used

bmad-agent-dev / bmad-dev-story

### Debug Log References

- Focused red test: `tests/test_health_status_monitoring.py` failed before implementation with missing backend state helpers and missing frontend indicator.
- Focused green test: `.venv/bin/pytest tests/test_health_status_monitoring.py` passed.
- Type check: `.venv/bin/mypy src/mtv_dl_web/main.py tests/test_health_status_monitoring.py` passed.
- Formatting: `.venv/bin/black src/mtv_dl_web/main.py tests/test_health_status_monitoring.py` passed; `npx prettier --write src/mtv_dl_web/frontend/index.html` unchanged.
- Full regression attempt: `MTV_DL_WEB_SKIP_DB_UPDATE=1 .venv/bin/pytest tests/` hung in pre-existing `tests/test_filter_validation.py::test_valid_operators`; isolated timeout reproduced the hang outside Story 1.5 code paths.

### Implementation Plan

1. Add test coverage for the Story 1.5 backend and UI states.
2. Track `Database.update_if_old()` with a thread-safe in-process flag.
3. Keep `/health` fast by reporting the tracked state instead of triggering database refresh work.
4. Add a header health indicator and poll `/health` to map backend states to UI labels/colors.
5. Validate with focused tests, formatting, and type checks.

### Completion Notes List

- [x] `/health` now returns `healthy`, `updating`, or `unhealthy` using a single `status` field.
- [x] Database refresh state is set around `Database.update_if_old()` and reset in a `finally` block.
- [x] Web UI now shows `online`, `updating`, or `offline` with green/yellow/red dots.
- [x] Health polling runs on page load and every 5 seconds.
- [x] Story 1.5 focused tests cover AC-15 through AC-18.

### Change Log

- 2026-05-11: Implemented Story 1.5 health status monitoring and marked ready for review.

### File List

- `src/mtv_dl_web/main.py` - Added database refresh tracking and non-blocking health status response.
- `src/mtv_dl_web/frontend/index.html` - Added three-state health indicator and `/health` polling.
- `tests/test_health_status_monitoring.py` - Added Story 1.5 backend and frontend tests.
- `_bmad-output/implementation-artifacts/1-5-improve-health-status-monitoring.md` - Added implementation story artifact.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` - Added Story 1.5 review status.
