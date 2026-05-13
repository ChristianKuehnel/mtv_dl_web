# Story 1.4: Load Service Configuration

Status: ready-for-dev

## Story

As a self-hosting user,
I want to configure service settings via a mounted file,
so that I can customize port, database path, and download options.

## Acceptance Criteria

1. **Given** a configuration file (for example `config.yaml`), **when** I start the service, **then** it loads settings (port, database path, target directories) from the file (FR-27, FR-28).
2. **Given** invalid configuration, **when** I start the service, **then** it rejects the config and logs a clear validation error (NFR-7).

## Tasks / Subtasks

- [ ] Implement configuration loading from mounted YAML file in startup path (AC: 1)
  - [ ] Ensure mounted file location is configurable and documented
  - [ ] Apply precedence rules: environment variables override file values
  - [ ] Keep startup deterministic; no implicit runtime reload unless explicitly designed
- [ ] Validate configuration values at startup before serving requests (AC: 2)
  - [ ] Reject invalid paths, invalid types, and invalid value ranges
  - [ ] Log actionable errors without secrets or stack traces in API responses
- [ ] Wire loaded config into existing runtime behavior (AC: 1)
  - [ ] Database path defaults to `~/.mtv_dl_web/filmliste.sqlite` unless overridden
  - [ ] Download target directories and feature flags map to existing request handling
- [ ] Add and update tests (AC: 1, 2)
  - [ ] Unit tests for parsing, precedence, and validation failures
  - [ ] Startup/integration tests proving app fails fast on invalid config

## Dev Notes

### Current State To Preserve

- `src/mtv_dl_web/main.py` currently reads several settings directly from environment and module globals.
- `src/mtv_dl_web/config/settings.py` exists but uses `pydantic.v1.BaseSettings` and currently hard-fails when default target directory is missing.
- Existing health/search/download flows must continue to work after config refactor.

### Required Implementation Guardrails

- Reuse existing `mtv_dl.Database` and `mtv_dl.Downloader`; do not add direct SQLite queries.
- Keep API contracts stable (`/health`, `/api/search`, `/api/download`, `/api/download/status*`).
- Preserve import/source-of-truth rules from Story 1.11 (`pyproject.toml` declared `mtv_dl` only).
- Keep single-user, no-auth architecture and mounted path deployment model.

### File Structure Requirements

- Backend runtime changes: `src/mtv_dl_web/main.py`.
- Configuration module changes: `src/mtv_dl_web/config/settings.py` (or same package path).
- Tests in `tests/` only.

### Testing Requirements

- Add focused tests for valid/invalid config load behavior and precedence.
- Verify no regression in health and search endpoints.
- Ensure lint/type/test commands remain compatible with project standards.

### Previous Story Intelligence

- Story 1.5/1.6 introduced concurrency-sensitive health and background refresh behavior; avoid startup/config changes that block these operations.
- Story 1.11 removed path-injection patterns; do not reintroduce alternate import resolution.
- Story 1.12 established CI/docs rigor; include explicit test coverage for config behavior.

### Git Intelligence Summary

- Recent commits favored test-first changes and explicit regression checks around health, concurrency, and dependency resolution.
- Keep changes small and verifiable; avoid broad rewrites unrelated to AC scope.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` Story 1.4]
- [Source: `_bmad-output/planning-artifacts/prd.md` FR-27, FR-28, NFR-7]
- [Source: `_bmad-output/planning-artifacts/architecture.md` Project Structure & Boundaries]
- [Source: `_bmad-output/project-context.md` Critical Implementation Rules]

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- To be filled during implementation.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.

### File List

- `src/mtv_dl_web/main.py` (update)
- `src/mtv_dl_web/config/settings.py` (update)
- `tests/...` (new/updated)
