# Story 6.3: Align Container Mount-Point Contract

Status: review

## Story

As a self-hosting user,
I want the container mount-point contract to be clear and consistent,
so that setup documentation matches actual runtime behavior.

## Acceptance Criteria

1. **Given** Milestone issue #41 expectation (`/data`, `/downloads`, `/config`), **when** I inspect deployment documentation and compose examples, **then** the documented mount-point contract is consistent and unambiguous.
2. **Given** implementation chooses exactly three mounts or a justified fourth mount, **when** I compare Dockerfile, compose, and README, **then** all references agree and explain persistence boundaries.
3. **Given** container restarts, **when** health and persistence checks run, **then** data required for operations (downloads, config, db/history) remains persistent under the documented mount contract.
4. **Given** test suite runs, **when** mount-point contract checks execute, **then** automated tests verify the chosen contract and prevent drift.

## Tasks / Subtasks

- [x] Choose and document the canonical mount strategy (AC: 1, 2)
  - [x] Option A: strict 3-mount contract (`/data`, `/downloads`, `/config`) and place app DB under `/data`
  - [x] Option B: keep 4-mount contract with explicit rationale and consistency updates
  - [x] Record decision in README and tests
- [x] Align runtime configuration with chosen contract (AC: 2, 3)
  - [x] Update `docker-compose.yml` mount list and env defaults
  - [x] Update Docker run / Podman run examples in README
  - [x] Ensure database path and target directory defaults match selected strategy
- [x] Update contract tests (AC: 4)
  - [x] Refresh `tests/test_docker_volumes.py` expectations
  - [x] Refresh README contract assertions in `tests/test_container_publish_docs.py`
- [x] Verify persistence behavior (AC: 3)
  - [x] Keep or add smoke/persistence checks tied to `/health` and restart behavior

## Dev Notes

### Current State (Must Understand Before Coding)

- Current docs and compose define four mounts: `/data`, `/downloads`, `/config`, `/home/appuser/.mtv_dl_web`.
- Issue #41 expects three mounts unless implementation intentionally differs and is fixed/documented.
- Current tests assert the four-mount contract; changing contract requires synchronized test updates.

### Required Change

- Make a single canonical mount-point contract and apply it consistently across Dockerfile/compose/README/tests.
- Ensure DB and history persistence still satisfy product requirements and restart behavior.

### What Must Be Preserved

- Persistent downloads and config behavior.
- Health endpoint readiness checks used in docs.
- No external services and self-hosted constraints.

### Technical Guardrails

- Avoid contradictory defaults between env vars and documentation.
- If reducing to three mounts, ensure DB path migration semantics are explicit to avoid user data surprises.
- Keep examples copy-paste runnable.

### Testing Requirements

- Contract tests must exactly match documented mount strategy.
- Include restart persistence assertion path (existing tests may already cover this; update wording and expectations accordingly).

### File Structure Requirements

- `docker-compose.yml`
- `Dockerfile`
- `README.md`
- `tests/test_docker_volumes.py`
- `tests/test_container_publish_docs.py`

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` Epic 6, Story 6.3]
- [Source: `_bmad-output/planning-artifacts/prd.md` FR-30, NFR-4, Journey 6]
- [Source: `README.md` container mount documentation]
- [Source: `docker-compose.yml` current mount and env contract]
- [Source: GitHub issue #41]

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- Chose Option A (three-mount contract) and aligned compose/docs/tests around `/data`, `/downloads`, `/config`.
- Updated environment defaults to use `/data/filmliste.sqlite` and `/downloads` in compose.
- Verified persistence/readiness guidance remains documented and contract tests pass.

### Completion Notes List

- [x] Canonical three-mount contract documented and applied consistently.
- [x] Container examples and compose mounts now match runtime contract.
- [x] Contract regression tests updated and passing.

### File List

- `docker-compose.yml`
- `README.md`
- `tests/test_docker_volumes.py`
- `tests/test_container_publish_docs.py`
