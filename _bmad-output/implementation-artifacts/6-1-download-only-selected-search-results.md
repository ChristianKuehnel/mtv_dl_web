# Story 6.1: Download Only Selected Search Results

Status: done

## Story

As a user,
I want "Download Selected Shows" to download only the shows I checked,
so that non-selected search results are never downloaded by mistake.

## Acceptance Criteria

1. **Given** search results are shown and one item is selected, **when** I click "Download Selected Shows", **then** only that selected show is downloaded/queued and no other result is started (#39).
2. **Given** multiple items are selected, **when** I trigger download, **then** only selected hashes are processed and each selected item is processed once.
3. **Given** selected IDs are empty or unknown, **when** backend receives the request, **then** it returns a clear 4xx error and starts no download job.
4. **Given** tests run, **when** selected-only behavior is validated, **then** automated tests prevent regression for #39.

## Tasks / Subtasks

- [x] Extend request contract to include selected identities (AC: 1, 2, 3)
  - [x] Add explicit request field for selected show hashes in `DownloadRequest`
  - [x] Keep backward-compatible validation behavior explicit (either reject old payload or document temporary compatibility path)
- [x] Wire frontend selection to backend request payload (AC: 1, 2)
  - [x] Send `Array.from(selectedShows)` (or equivalent) with the download request
  - [x] Keep existing status messaging and button state behavior intact
- [x] Restrict backend download set to selected hashes only (AC: 1, 2, 3)
  - [x] Search/filter using existing logic first, then intersect with selected hashes
  - [x] Return 400/404 for empty intersection or unknown selected hashes
  - [x] Preserve thread-safe updates to `active_downloads`
- [x] Add focused regression tests (AC: 4)
  - [x] Test one-selected-item path
  - [x] Test multi-selected-items path
  - [x] Test unknown/empty selection rejection path

## Dev Notes

### Current State (Must Understand Before Coding)

- `src/mtv_dl_web/frontend/index.html` already tracks user selection via `selectedShows` but currently posts only `filters` to `/api/download`; this is the root cause of #39.
- `src/mtv_dl_web/main.py` currently resolves `shows = list(db_conn.filtered(download_request.filters))` and downloads all returned shows, regardless of UI selection.
- `src/mtv_dl_web/main.py` already has locking patterns around `active_downloads` and background task scheduling; preserve them.

### Required Change

- Introduce explicit selected-hash payload from UI to API.
- Ensure backend only schedules downloads for selected hashes that are present in the filtered result set.
- Keep behavior deterministic when selected hashes are stale, missing, or duplicated.

### What Must Be Preserved

- Existing filter validation (`validate_filters`) and search semantics.
- Existing health/refresh responsiveness and background-task model.
- Existing error handling style with `HTTPException` and non-sensitive messages.

### Technical Guardrails

- Reuse `mtv_dl.Database.filtered()`; do not implement ad-hoc filtering in SQL.
- Keep route handlers async and maintain current lock usage around shared mutable state.
- Do not redesign queue architecture in this story; scope is selected-item correctness only.

### Testing Requirements

- Add or extend tests in `tests/` (likely `tests/test_fastapi_backend.py` or a new targeted file) to assert selected-only download scheduling.
- Mock database rows with distinct hashes to prove non-selected rows are not scheduled.
- Assert both response payload and resulting `active_downloads`/scheduled IDs.

### File Structure Requirements

- `src/mtv_dl_web/frontend/index.html` (selection payload wiring)
- `src/mtv_dl_web/main.py` (request model + selected-only scheduling)
- `tests/*.py` (regression tests)

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` Epic 6, Story 6.1]
- [Source: `_bmad-output/planning-artifacts/prd.md` FR-6, SC-3, Journey 1]
- [Source: `src/mtv_dl_web/frontend/index.html` selection and download request flow]
- [Source: `src/mtv_dl_web/main.py` `/api/download` implementation]
- [Source: GitHub issue #39]

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- Added `selected_hashes` request support and selected-only scheduling in `/api/download`.
- Verified frontend now sends selected hashes in request payload.
- Added selected-download regression coverage and executed targeted Epic 6 tests.

### Completion Notes List

- [x] Download endpoint now validates and deduplicates selected hashes before scheduling jobs.
- [x] Frontend payload includes selected hashes while preserving existing UX/status flow.
- [x] Regression tests added for one, multiple, and invalid selected-hash scenarios.

### File List

- `src/mtv_dl_web/frontend/index.html`
- `src/mtv_dl_web/main.py`
- `tests/test_download_selected.py`
