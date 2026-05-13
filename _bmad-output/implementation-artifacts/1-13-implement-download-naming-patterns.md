# Story 1.13: Implement download naming patterns

Status: ready-for-dev

## Story

As a user,
I want downloads to use the same naming and folder behavior as `mtv_dl`,
so that files land in the expected shared folder with recognizable names.

## Acceptance Criteria

1. Given a queued item starts downloading, when the backend delegates to `mtv_dl.Downloader`, then it uses `mtv_dl` naming and folder structure behavior rather than writing `download.mp4` in the project root (FR-13).
2. Given a completed download, when the system verifies the files, then all file names match the configured naming behavior and files are located under the configured target directory (FR-14, AC-22).
3. Queue status shows the resulting file path for completed downloads when `mtv_dl` exposes or the service can safely determine it.

## Tasks / Subtasks

- [ ] Analyze `mtv_dl`'s current naming patterns and folder structure (AC: 1, 2)
  - [ ] Examine existing mtv_dl CLI behavior for file naming
  - [ ] Document current naming conventions and folder organization
- [ ] Ensure the download handler delegates naming and folder decisions to `mtv_dl.Downloader` (AC: 1)
  - [ ] Remove any web-app fallback that writes `download.mp4` in the project root
  - [ ] Pass target directory and supported options in the format expected by `mtv_dl`
  - [ ] Do not reimplement filename sanitization or series naming in the web app
- [ ] Ensure files are saved to correct target directory (AC: 2)
  - [ ] Integrate with existing configuration for target directory
  - [ ] Verify directory exists and is writable
  - [ ] Verify no completed download falls back to the project root
- [ ] Add validation to verify naming behavior after download completion (AC: 2)
  - [ ] Check that completed files match `mtv_dl` output behavior for the configured target directory
  - [ ] Verify file location matches configured target directory
  - [ ] Add validation to queue completion logic
- [ ] Update queue status to include file paths when available (AC: 3)
  - [ ] Modify queue status response to include downloaded file paths
  - [ ] Ensure completed downloads show full path information

## Dev Notes

- Must preserve existing `mtv_dl` behavior for file organization and naming
- Use `mtv_dl`'s existing Database and Downloader classes from the dependency resolved by `pyproject.toml`
- Downloads are handled through BackgroundTasks in FastAPI
- Configuration is loaded from mounted YAML files
- Do not hard-code series or non-series filename patterns in the web app unless `mtv_dl` exposes them as configuration

### Project Structure Notes

- Download handler: `src/mtv_dl_web/main.py` - FastAPI endpoints
- Configuration: `src/config.py` - Load service settings
- Queue management: BackgroundTasks integration
- File operations: Use existing `mtv_dl` downloader behavior

### References

- PRD: FR-13, FR-14, AC-22
- Architecture: FastAPI backend, BackgroundTasks for downloads
- mtv_dl integration: `pyproject.toml` dependency and installed `mtv_dl` package

## Dev Agent Record

### Agent Model Used

mistral/devstral-small-latest

### Debug Log References


### Completion Notes List


### File List
