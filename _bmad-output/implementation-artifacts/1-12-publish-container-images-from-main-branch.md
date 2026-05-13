# Story 1.12: Publish Container Images from Main Branch

Status: done

## Story

As a self-hosting user,
I want a project-published container image built from main,
so that installation does not require building the image locally.

## Acceptance Criteria

1. **Given** changes land on the main branch,
   **When** the GitHub workflow runs successfully,
   **Then** it builds and publishes a container image for the project (FR-39).

2. **Given** the image is published,
   **When** I read the documentation,
   **Then** I can find the image location and run it with documented configuration, data, and download mounts (FR-30, FR-39).

3. **Given** the documented image is run with the required mounts,
   **When** I call the readiness endpoint,
   **Then** it reports ready and persists mounted data across restart (FR-30, FR-31).

## Tasks / Subtasks

- [x] Add main-branch image publish workflow (AC: 1)
  - [x] Add GitHub Actions workflow that builds container image on pushes to `main`
  - [x] Configure publish target and tags for project image
  - [x] Ensure workflow permissions support image publishing
- [x] Document published image usage for self-hosting (AC: 2)
  - [x] Document image registry location and tags
  - [x] Document `docker run` mounts for config, data, downloads, and `~/.mtv_dl_web`
  - [x] Document equivalent `podman run` example
- [x] Add readiness and persistence verification guidance and tests (AC: 3)
  - [x] Document readiness endpoint verification command
  - [x] Document data persistence verification across restart with mounted volumes
  - [x] Add/extend tests that validate workflow and documentation requirements

## Dev Notes

- Keep CI behavior intact; add a dedicated publish workflow rather than overloading CI checks.
- Use GitHub Container Registry (`ghcr.io`) for published image distribution.
- Preserve existing mount strategy (`/data`, `/downloads`, `/config`, `/home/appuser/.mtv_dl_web`) in docs.
- Readiness endpoint for this service is `GET /health`.

### Project Structure Notes

- CI workflows: `.github/workflows/`
- Container runtime docs: `README.md`
- Container runtime config: `Dockerfile`, `docker-compose.yml`
- Tests: `tests/`

### References

- `_bmad-output/planning-artifacts/epics.md#Story-1.12`
- `_bmad-output/planning-artifacts/prd.md` (FR-30, FR-31, FR-39)

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- Created story artifact from epic because 1.12 implementation file was missing.
- Added test-first coverage for publish workflow and README requirements; initial run failed as expected before implementation.

### Implementation Plan

1. Add a new GitHub Actions workflow to publish image on `main`.
2. Update README with published image usage and mount documentation.
3. Add tests that verify workflow trigger/publish config and README runtime guidance.
4. Run tests and quality checks.

### Completion Notes List

- [x] Added `.github/workflows/publish-container.yml` to publish GHCR images on `main` and manual dispatch.
- [x] Added README section for prebuilt GHCR usage with Docker and Podman mount examples.
- [x] Documented readiness (`GET /health`) and persistence checks across container restart.
- [x] Added tests in `tests/test_container_publish_docs.py` covering workflow trigger/publish semantics and docs requirements.
- [x] Full test suite passed (`./scripts/tests.sh`).
- [x] Linting and quality checks passed (`PATH="/tmp:$PATH" ./scripts/linting.sh --check`, with temporary hadolint binary).

### File List

- `.github/workflows/publish-container.yml` - New GitHub Actions workflow to build and publish container images from `main`.
- `README.md` - Added GHCR image usage, Docker/Podman examples, and readiness/persistence verification guidance.
- `tests/test_container_publish_docs.py` - Added tests validating publish workflow configuration and documentation requirements.
- `_bmad-output/implementation-artifacts/1-12-publish-container-images-from-main-branch.md` - Story execution updates.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` - Story status transition updates.

### Change Log

- 2026-05-13: Story artifact created from epic context.
- 2026-05-13: Implemented main-branch GHCR publish workflow and added documentation for running prebuilt image with required mounts.
- 2026-05-13: Added publish/docs verification tests and validated full test suite plus linting checks.
