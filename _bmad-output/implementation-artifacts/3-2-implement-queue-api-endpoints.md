# Story 3.2: Implement Queue API Endpoints

Status: done

## Story

As a user,
I want to add/remove downloads via API,
So that I can manage my download queue.

## Acceptance Criteria

1. **Given** a video ID, **when** I call `POST /queue` with `{ "video_id": "123" }`, **then** it adds the video to the queue (FR-15).
2. **Given** a pending queue item, **when** I call `DELETE /queue/{id}`, **then** it removes the item (FR-18).
3. **Given** malformed request payloads or unsupported IDs, **when** queue endpoints are called, **then** the API returns structured 4xx errors without stack traces (NFR-1, NFR-8).

## Tasks / Subtasks

- [x] Add queue request/response models in `src/mtv_dl_web/main.py`
  - [x] Add a request model for `POST /queue`
  - [x] Add response shape for queue listing and delete actions
- [x] Implement queue endpoints in `src/mtv_dl_web/main.py`
  - [x] Add `POST /queue` to enqueue one item
  - [x] Add `GET /queue` to list queue entries and states
  - [x] Add `DELETE /queue/{id}` to remove only pending entries
- [x] Keep shared-state access thread-safe
  - [x] Guard queue mutations with lock discipline compatible with existing `active_downloads_lock`
  - [x] Keep API responsive during refresh/download activity
- [x] Add/extend API tests in `tests/`
  - [x] Happy path add/list/remove
  - [x] Validation and error-path tests

## Retrospective Guardrails

- Dependency gate: do not bypass `mtv_dl` data contracts; preserve existing search/download object shapes.
- Concurrency gate: all queue mutations must be lock-protected to avoid race conditions under concurrent requests.
- Regression gate: existing `/api/search`, `/api/download`, and `/api/download/status*` behavior must remain unchanged.

## Dev Notes

### Current State and Required Change

- `src/mtv_dl_web/main.py` currently exposes `/api/search`, `/api/download`, and `/api/download/status*`, but no `/queue` endpoints.
- The app already has in-memory state (`download_queue`, `active_downloads`) and lock primitives; extend these instead of introducing a second queue system.
- Existing frontend calls `/api/download` directly; this story introduces queue APIs without breaking current download/status routes.

### Architecture and Compliance Requirements

- Keep implementation in `src/mtv_dl_web/main.py` and tests in `tests/`.
- Use FastAPI + Pydantic models; all handlers remain `async def`.
- Maintain structured errors and avoid leaking internals in error text.
- Preserve single-active-download strategy for follow-up Story 3.3.

### Library/Framework Requirements

- Use currently pinned stack from project context: FastAPI, Pydantic v2, pytest, mypy strict, black.
- Continue importing `Database` and `Downloader` from `mtv_dl.mtv_dl` via `pyproject.toml` dependency source.

### Testing Requirements

- Add endpoint tests for `POST /queue`, `GET /queue`, `DELETE /queue/{id}`.
- Include one concurrency-oriented test (parallel add/remove/list) to confirm stable state handling.
- Validate 4xx cases for invalid payloads and deleting non-pending/non-existent items.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Epic-3-Download-Queue-Management]
- [Source: _bmad-output/planning-artifacts/epics.md#Story-3.2-Implement-Queue-API-Endpoints]
- [Source: _bmad-output/planning-artifacts/prd.md#Queue]
- [Source: _bmad-output/planning-artifacts/architecture.md#API--Communication-Patterns]
- [Source: _bmad-output/project-context.md#Critical-Implementation-Rules]

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- `pytest tests/test_queue_api.py tests/test_search_ui.py tests/test_download_selected.py`
- `pytest` (fails in this environment due missing `mtv_dl` dependency during collection in unrelated suites)

### Completion Notes List

- [x] Added queue API request/response models and `/queue` + `/api/queue` endpoints with 4xx error handling.
- [x] Added lock-protected queue add/list/remove behavior and pending-only deletion rules.
- [x] Added queue API tests for happy-path, validation, and status constraints.

### File List

- `src/mtv_dl_web/main.py`
- `tests/test_queue_api.py`

## Change Log

- 2026-05-14: Implemented queue API models/endpoints, thread-safe queue operations, and API coverage tests.
