# Story 6.2: Enforce Download Target and mtv_dl Naming Outcome

Status: ready-for-dev

## Story

As a self-hosting user,
I want downloads to end up in the configured shared target directory with `mtv_dl` naming behavior,
so that files do not appear as `download.mp4` in the project root.

## Acceptance Criteria

1. **Given** a download request is started, **when** backend delegates to `mtv_dl.Downloader.download(...)`, **then** naming/folder behavior is delegated to `mtv_dl` and no custom fallback writes to project root (#16).
2. **Given** a target directory is configured, **when** download completes, **then** returned output path is validated to reside inside the configured target boundary (including resolved-path checks).
3. **Given** the returned path is missing or outside target boundary, **when** status is finalized, **then** download is marked failed with clear non-sensitive message and no false "completed" state is emitted.
4. **Given** container defaults are used, **when** user follows docs/compose defaults, **then** target location aligns with shared mounted storage (`/downloads` or documented equivalent).
5. **Given** regression tests run, **when** success/failure path cases are executed, **then** placement validation and status transitions are covered.

## Tasks / Subtasks

- [ ] Harden target-path handling in backend (AC: 1, 2, 3)
  - [ ] Resolve configured target path safely (`expanduser`, `resolve` where appropriate)
  - [ ] Validate downloader returned path is under target root before marking completed
  - [ ] Keep failure branch explicit for out-of-bound or missing path
- [ ] Align default target behavior for containerized usage (AC: 4)
  - [ ] Verify and update defaults in frontend/config/compose where needed
  - [ ] Ensure docs and runtime defaults do not imply project-root output
- [ ] Preserve existing mtv_dl integration contract (AC: 1)
  - [ ] Continue using `Downloader.download(...)` quality tuple + option pass-through
  - [ ] Do not reimplement naming logic in web layer
- [ ] Add regression tests (AC: 5)
  - [ ] Success case: valid in-target output path
  - [ ] Failure case: out-of-target output path
  - [ ] Failure case: missing/None output path

## Dev Notes

### Current State (Must Understand Before Coding)

- `src/mtv_dl_web/main.py` already calls `Downloader.download(...)` and stores `file_path` when returned.
- Current code does not enforce strict target-boundary validation before setting status to `completed`.
- `docker-compose.yml` currently sets `TARGET_DIRECTORY=~/Downloads/mtv_dl` while mounts expose `/downloads`; this mismatch can confuse runtime expectations.
- `src/mtv_dl_web/frontend/index.html` default target is currently `./downloads`, which is ambiguous in container context.

### Required Change

- Add explicit path-boundary validation of downloader result prior to completion.
- Harmonize defaults to mounted shared location for container flows.
- Preserve delegation to `mtv_dl` naming logic as the source of truth.

### What Must Be Preserved

- Existing downloader quality map behavior and option pass-through.
- Existing lock-protected shared-state updates.
- Existing no-direct-database-query constraints.

### Technical Guardrails

- Treat symlink/path traversal carefully; compare resolved paths.
- Keep failure messages actionable but non-sensitive.
- Avoid introducing ad-hoc file-writing fallbacks in backend.

### Testing Requirements

- Use mocked downloader return values to simulate valid and invalid paths.
- Verify final status and `file_path` fields for completed vs failed cases.
- Add a configuration/default test to ensure container-facing defaults are coherent.

### File Structure Requirements

- `src/mtv_dl_web/main.py` (download completion and path validation)
- `src/mtv_dl_web/frontend/index.html` (default target UX value if needed)
- `src/mtv_dl_web/config/settings.py` and/or `docker-compose.yml` (default target alignment)
- `README.md` (deployment guidance consistency)
- `tests/*.py` (regression coverage)

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` Epic 6, Story 6.2]
- [Source: `_bmad-output/planning-artifacts/prd.md` FR-7, FR-9, FR-13, FR-14, Journey 1]
- [Source: `_bmad-output/implementation-artifacts/1-13-implement-download-naming-patterns.md` review findings]
- [Source: `src/mtv_dl_web/main.py` downloader integration path]
- [Source: GitHub issue #16]

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- Pending implementation

### Completion Notes List

- [ ] Ultimate context engine analysis completed - comprehensive developer guide created

### File List

- `src/mtv_dl_web/main.py` (planned)
- `src/mtv_dl_web/frontend/index.html` (planned)
- `src/mtv_dl_web/config/settings.py` (planned)
- `docker-compose.yml` (planned)
- `README.md` (planned)
- `tests/` (planned)
