# Story 1.11: Consolidate mtv_dl Dependency Integration

Status: done

## Story

As a maintainer,
I want `pyproject.toml` to be the single source of truth for the `mtv_dl` version,
So that local, test, and container behavior always use the same declared dependency version.

## Acceptance Criteria

1. **Given** the project dependency configuration,
**When** dependencies are installed,
**Then** `mtv_dl` is installed from the version declared in `pyproject.toml`, with no alternate dependency declaration overriding it (FR-38).

2. **Given** application code imports `mtv_dl`,
**When** the import resolves in local, test, or container execution,
**Then** it resolves to the installed dependency version declared in `pyproject.toml`, not to a different vendored, submodule, or path-injected copy (FR-38).

3. **Given** the repository is inspected,
**When** duplicate vendored or submodule `mtv_dl` copies are found,
**Then** they are removed or made inactive so they cannot conflict with the `pyproject.toml` dependency version (FR-38).

4. **Given** local tests and container startup run,
**When** `mtv_dl` is imported,
**Then** both environments import the same `pyproject.toml`-declared dependency version.

## Tasks / Subtasks

- [x] Consolidate mtv_dl dependency management
  - [x] Identify all current mtv_dl dependency declarations in the codebase
  - [x] Remove duplicate or conflicting vendored/submodule copies
  - [x] Ensure pyproject.toml is the single source of truth
- [x] Verify dependency resolution
  - [x] Test local development environment
  - [x] Test containerized environment
  - [x] Validate import paths are correct
- [x] Update documentation and configuration
  - [x] Remove outdated mtv_dl import configurations
  - [x] Update any relevant documentation
- [x] Run comprehensive tests
  - [x] Run all existing tests to ensure no regressions
  - [x] Test mtv_dl import functionality in all contexts

### Review Findings

- [x] [Review][Patch] Enforce index-only `mtv-dl` dependency source [`pyproject.toml`] [`tests/test_uv_setup.py`]
- [x] [Review][Patch] Add explicit parity verification for local/test/container `mtv_dl` resolution [`pyproject.toml`] 
- [x] [Review][Patch] Remove stale path-injection comments in runtime import section to avoid misleading future maintenance [`src/mtv_dl_web/main.py`]
- [x] [Review][Patch] Make `mtv_dl` import test fail on `ImportError` [`tests/test_uv_setup.py:46`]
- [x] [Review][Patch] Add explicit local/test/container parity assertion for dependency source/version [`tests/test_uv_setup.py:38`]

## Dev Notes

### Project Structure Notes

- The project now relies exclusively on the `mtv_dl` version declared in `pyproject.toml`
- All imports resolve to the declared dependency, not vendored copies
- The vendored mtv_dl submodule has been removed and replaced with standard dependency management

### References

- [Source: spec/sw_architecture.md#Dependency-Management]
- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.11]
- [Source: _bmad-output/planning-artifacts/prd.md#FR-38]

## Dev Agent Record

### Agent Model Used

bmad-dev-story

### Debug Log References

N/A

### Implementation Plan

1. First, identified all current mtv_dl dependency declarations in the codebase
2. Removed duplicate or conflicting vendored/submodule copies
3. Ensured that pyproject.toml is the single source of truth for mtv_dl version
4. Removed the path-based editable install and relied solely on the pip-installed version
5. Updated the import mechanism in `src/mtv_dl_web/main.py` to not manually modify sys.path
6. Verified local development and containerized environments properly resolve the dependency
7. Ran comprehensive tests to ensure no regressions

### Completion Notes List

- [x] Dependency management consolidated
- [x] All mtv_dl imports resolve to pyproject.toml declared version
- [x] Duplicate vendored/submodule copies removed
- [x] Documentation updated
- [x] All tests pass
- [x] Explicit parity verification added for local/test/container mtv_dl resolution

### Change Log

- 2026-05-13: Initial story creation and setup
- 2026-05-13: Updated pyproject.toml to use standard dependency declaration
- 2026-05-13: Modified main.py to remove manual sys.path insertion for mtv_dl
- 2026-05-13: Verified all functionality works with standard dependency
- 2026-05-13: All tests pass confirming no regressions
- 2026-05-13: Added explicit parity verification for local/test/container mtv_dl resolution

### File List

- `pyproject.toml` - Updated dependency management to remove path-based editable install
- `src/mtv_dl_web/main.py` - Removed manual sys.path insertion for mtv_dl
- `tests/test_uv_setup.py` - Added explicit parity verification for mtv_dl resolution
