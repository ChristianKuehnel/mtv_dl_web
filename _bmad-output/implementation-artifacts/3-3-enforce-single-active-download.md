# Story 3.3: Enforce Single Active Download

Status: ready-for-dev

## Story

As a user,
I want only one download to run at a time,
So that my system resources are not overwhelmed.

## Acceptance Criteria

1. **Given** an active download, **when** I add another item to the queue, **then** it remains `pending` until the active download completes (FR-16).
2. **Given** queued items with mixed states, **when** the active item transitions to `completed` or `failed`, **then** the next pending item begins automatically.
3. **Given** status polling during active downloads, **when** queue state is requested, **then** exactly one item is `downloading` at any time.

## Tasks / Subtasks

- [ ] Add queue-processing orchestration in `src/mtv_dl_web/main.py`
  - [ ] Add helper to promote one `pending` item to `downloading`
  - [ ] Ensure promotion runs after enqueue and after completion/failure transitions
- [ ] Integrate single-active rules with existing download background flow
  - [ ] Preserve current `Downloader.download()` invocation behavior
  - [ ] Avoid deadlocks between queue lock and `active_downloads_lock`
- [ ] Add tests in `tests/`
  - [ ] Verify second item stays pending while first downloads
  - [ ] Verify automatic progression to next pending item
  - [ ] Verify failed active item still unblocks queue progression

## Retrospective Guardrails

- Concurrency gate: hold locks for minimal scope; never block event loop with long lock holds.
- Behavior gate: preserve existing download option mapping (`quality_map`, subtitles/NFO/MKV flags).
- Failure gate: queue must recover from a failed item and continue with next pending item.

## Dev Notes

### Current State and Required Change

- Current implementation (`/api/download`) schedules one background task per matched show immediately, enabling parallel downloads.
- Story requires serial execution semantics across queued items.
- Reuse existing in-memory queue/status structures; avoid introducing external brokers or databases.

### What Must Be Preserved

- Existing search, health, database refresh, and status APIs continue working under load.
- Existing `Downloader.download()` behavior and quality ordering stay intact.
- Existing error handling style (`HTTPException` + logged failures) remains consistent.

### Architecture and Compliance Requirements

- Keep single-user, no-external-service design.
- Do not bypass `mtv_dl`; no direct SQLite download-state persistence in this story.
- Keep code in `src/mtv_dl_web/main.py`, tests in `tests/`.

### Testing Requirements

- Add deterministic tests around queue state transitions (`pending` -> `downloading` -> terminal).
- Assert that concurrent enqueue calls cannot create two active download workers.
- Cover both success and exception paths in background processing.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-3.3-Enforce-Single-Active-Download]
- [Source: _bmad-output/planning-artifacts/prd.md#FR-16]
- [Source: src/mtv_dl_web/main.py]
- [Source: _bmad-output/project-context.md#Development-Workflow-Rules]

## Dev Agent Record

### Agent Model Used

TBD

### Debug Log References

TBD

### Completion Notes List

- [ ] Ultimate context engine analysis completed - comprehensive developer guide created

### File List

- `src/mtv_dl_web/main.py` (planned)
- `tests/test_api.py` (planned)
- `tests/test_integration.py` (planned)
