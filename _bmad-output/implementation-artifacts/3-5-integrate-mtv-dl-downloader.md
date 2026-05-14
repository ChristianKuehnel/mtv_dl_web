# Story 3.5: Integrate mtv_dl.Downloader

Status: done

## Story

As a user,
I want downloads to use existing `mtv_dl` behavior,
So that my files are saved correctly.

## Acceptance Criteria

1. **Given** a queued item, **when** it starts downloading, **then** it uses `mtv_dl.Downloader` with configured options (FR-7, FR-8, FR-9).
2. **Given** subtitle/NFO/MKV options are configured, **when** a queue item runs, **then** those options are passed through without behavior drift (FR-10, FR-11, FR-12).
3. **Given** downloads complete in containerized runtime, **when** file output is written, **then** files persist in configured target directory and follow existing naming behavior (FR-13, FR-14, FR-40).

## Tasks / Subtasks

- [x] Align queue worker execution with `mtv_dl.Downloader` usage
  - [x] Ensure queued item payload contains all downloader-required metadata
  - [x] Reuse existing quality tuple mapping and option flags
- [x] Validate path and target-directory handling
  - [x] Ensure configured target path is resolved/created safely
  - [x] Confirm no fallback to unintended project-root outputs
- [x] Harden failure handling and status reporting
  - [x] Record failed state with useful non-sensitive message
  - [x] Ensure retries are not implicit in MVP
- [x] Add tests and smoke checks
  - [x] Integration-style check for downloader invocation contract
  - [x] Container/path persistence check hooks in smoke test flow

## Retrospective Guardrails

- Dependency gate: imports must continue to resolve to `mtv_dl` from `pyproject.toml` version source.
- Behavior gate: do not reimplement downloader internals or naming logic.
- Safety gate: preserve non-blocking health/status responsiveness during queue downloads.

## Dev Notes

### Current State and Required Change

- Current `download_show_background` already calls `Downloader(show_data).download(...)` with mapped quality tuple and option flags.
- Story focus is integration hardening in queue-driven flow so downloader invocation remains canonical while queue semantics evolve.
- Ensure queue item structure and transitions do not strip metadata required by `mtv_dl`.

### What Must Be Preserved

- Existing quality precedence behavior (`best/low/medium/high` mappings).
- Existing include flags (`include_subtitles`, `include_nfo`, `merge_to_mkv`) pass-through.
- Existing exception logging and terminal status transitions.

### Architecture and Compliance Requirements

- No alternate downloader implementation or direct datastore shortcuts.
- Keep data/download path behavior aligned with mounted-volume model.
- Maintain FastAPI + background-task architecture and project layout.

### Testing Requirements

- Verify downloader call arguments from queue context are correct and complete.
- Verify output path behavior under configured target directories.
- Verify failed downloader runs produce `failed` queue/download state and useful user-facing message.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-3.5-Integrate-mtv_dl.Downloader]
- [Source: _bmad-output/planning-artifacts/prd.md#Downloads]
- [Source: _bmad-output/project-context.md#Critical-Dont-Miss-Rules]
- [Source: src/mtv_dl_web/main.py]

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- `pytest tests/test_download_selected.py tests/test_queue_api.py`

### Completion Notes List

- [x] Queue worker now starts from queued payload metadata and preserves downloader option pass-through.
- [x] Preserved quality mapping and target path safety checks in queue-driven download flow.
- [x] Verified failure reporting and non-retry behavior in queue progression tests.

### File List

- `src/mtv_dl_web/main.py`
- `tests/test_download_selected.py`
- `tests/test_queue_api.py`

## Change Log

- 2026-05-14: Integrated queue processing with canonical `mtv_dl.Downloader` invocation contract and status hardening.
