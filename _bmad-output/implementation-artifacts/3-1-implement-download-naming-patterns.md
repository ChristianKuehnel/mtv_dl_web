# Story 3.1: Implement download naming patterns

Status: ready-for-dev

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

- [ ] Analyze mtv_dl's current naming patterns and folder structure (AC: 1, 4)
  - [ ] Examine existing mtv_dl CLI behavior for file naming
  - [ ] Document current naming conventions and folder organization
- [ ] Implement naming pattern logic in download handler (AC: 1, 2)
  - [ ] Create function to generate filenames based on content type (series vs non-series)
  - [ ] Add filename sanitization (replace spaces with underscores, remove special characters)
  - [ ] Handle edge cases (empty titles, missing episode info)
- [ ] Ensure files are saved to correct target directory (AC: 3, 4)
  - [ ] Integrate with existing configuration for target directory
  - [ ] Verify directory exists and is writable
  - [ ] Implement flat folder structure
- [ ] Add validation to verify naming patterns after download completion (AC: 6)
  - [ ] Create validation function to check filename patterns
  - [ ] Verify file location matches configured target directory
  - [ ] Add validation to queue completion logic
- [ ] Update queue status to include file paths (AC: 5)
  - [ ] Modify queue status response to include downloaded file paths
  - [ ] Ensure completed downloads show full path information

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


### Completion Notes List


### File List