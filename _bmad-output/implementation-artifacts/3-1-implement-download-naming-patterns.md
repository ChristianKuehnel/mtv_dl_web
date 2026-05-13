# Story 3.1: Implement download naming patterns

Status: done

## Story

As a user,
I want downloads to follow consistent naming patterns and folder structure,
so that my files are organized correctly and match the existing mtv_dl CLI behavior.

## Acceptance Criteria

1. Downloads follow the specified naming patterns: `{title} - {episode_title}.{ext}` for series content and `{title}.{ext}` for non-series content
2. Filenames have spaces replaced by underscores and special characters sanitized
3. Files are saved to the configured target directory
4. Files are organized in a flat folder structure under the configured target directory
5. Queue status shows correct file paths for completed downloads
6. AC-22 verification passes: Given a completed download, when the system verifies the files, then all file names match the configured naming pattern and files are located in the configured target directory

## Tasks / Subtasks

- [x] Analyze mtv_dl's current naming patterns and folder structure (AC: 1, 4)
  - [x] Examine existing mtv_dl CLI behavior for file naming
  - [x] Document current naming conventions and folder organization
- [x] Implement naming pattern logic in download handler (AC: 1, 2)
  - [x] Create function to generate filenames based on content type (series vs non-series)
  - [x] Add filename sanitization (replace spaces with underscores, remove special characters)
  - [x] Handle edge cases (empty titles, missing episode info)
- [x] Ensure files are saved to correct target directory (AC: 3, 4)
  - [x] Integrate with existing configuration for target directory
  - [x] Verify directory exists and is writable
  - [x] Implement flat folder structure
- [x] Add validation to verify naming patterns after download completion (AC: 6)
  - [x] Create validation function to check filename patterns
  - [x] Verify file location matches configured target directory
  - [x] Add validation to queue completion logic
- [x] Update queue status to include file paths (AC: 5)
  - [x] Modify queue status response to include downloaded file paths
  - [x] Ensure completed downloads show full path information

## Dev Notes

- Must preserve existing mtv_dl behavior for file organization and naming
- Use mtv_dl's existing Database and Downloader classes
- Downloads are handled through BackgroundTasks in FastAPI
- Configuration is loaded from mounted YAML files
- Series content: `{title} - {episode_title}.{ext}` pattern
- Non-series content: `{title}.{ext}` pattern
- Filename sanitization: replace spaces with underscores, remove special characters

### Project Structure Notes

- Download handler: `src/main.py` - FastAPI endpoints
- Configuration: `src/config.py` - Load service settings
- Queue management: BackgroundTasks integration
- File operations: Use existing mtv_dl downloader behavior

### References

- PRD: FR-13, FR-14, AC-22
- Architecture: FastAPI backend, BackgroundTasks for downloads
- mtv_dl integration: `src/mtv_dl/database.py`, `src/mtv_dl/downloader.py`

## Dev Agent Record

### Agent Model Used

mistral/devstral-small-latest

### Debug Log References

- `pytest tests/test_download_naming_patterns.py -q`
- `pytest -q`
- `bash scripts/linting.sh`

### Completion Notes List

- Analyzed `Downloader._move_to_user_target` in mtv_dl and documented how naming/placeholders are currently resolved via escaped metadata and target path templating.
- Added explicit naming helpers in the FastAPI layer for sanitized series/non-series naming rules and edge-case fallbacks.
- Added flat-target enforcement that moves completed downloads into configured target root and normalizes filename pattern.
- Added post-download validation to ensure completed files both match naming conventions and remain in configured target directory.
- Queue status now stores validated, final absolute file path for completed downloads.
- Added focused automated tests for naming generation, sanitization, validation, and end-to-end background status behavior.

### File List

- `src/mtv_dl_web/main.py`
- `tests/test_download_naming_patterns.py`

### Change Log

- 2026-05-12: Implemented download naming pattern enforcement, flat target placement, post-download validation, and queue file path verification with automated tests.
- 2026-05-13: Fixed episode title assignment bug in filename generation function.
