# Story 1.13: Implement Download Naming Patterns

Status: ready-for-dev

## Story

As a user,
I want downloads to use the same naming and folder behavior as `mtv_dl`,
so that files land in the expected shared folder with recognizable names.

## Acceptance Criteria

1. **Given** a queued item starts downloading, **when** the backend delegates to `mtv_dl.Downloader`, **then** it uses `mtv_dl` naming and folder structure behavior rather than writing `download.mp4` in the project root (FR-13).
2. **Given** a completed download, **when** the system verifies the files, **then** file names match configured naming behavior and files are under configured target directory (FR-14, AC-22).

## Tasks / Subtasks

- [ ] Verify downloader integration uses `mtv_dl.Downloader.download(...)` as source of naming truth (AC: 1)
  - [ ] Remove or block any fallback output path behavior to repository root
  - [ ] Pass target and options exactly in formats expected by mtv_dl
- [ ] Add completion-time verification for file placement and naming expectations (AC: 2)
  - [ ] Store resulting path in queue/download status when available
  - [ ] Validate resulting path stays under configured target directory
- [ ] Add regression tests for naming/folder behavior (AC: 1, 2)
  - [ ] Include failure-path tests where mtv_dl returns no path or errors

## Dev Notes

- In `main.py`, download execution already calls `Downloader(...).download(...)` and stores `file_path`; keep this behavior central.
- Ensure target directory source is configuration-driven and not silently replaced by relative defaults.
- Preserve Story 1.11 dependency source rules; no vendored/path-injected `mtv_dl` implementations.
- Do not reimplement mtv_dl naming rules in web app code.

### File Structure Requirements

- `src/mtv_dl_web/main.py` (download workflow/status updates)
- `tests/` (download naming placement tests)

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` Story 1.13]
- [Source: `_bmad-output/planning-artifacts/prd.md` FR-13, FR-14, AC-22]
- [Source: `_bmad-output/project-context.md` Critical Don't-Miss Rules]

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
