# Story 2.3: Build Search UI

Status: review

## Story

As a user,
I want a search form and results list in the UI,
So that I can search without using the API directly.

## Acceptance Criteria

1. **Given** the search page, **when** I enter filters and submit, **then** results display metadata (title, channel, size, etc.) (FR-5)
2. **Given** no results, **when** I search, **then** the UI shows a "No results" message
3. **Given** a refresh is running in the backend, **when** I submit a search in the UI, **then** the UI remains interactive, shows loading/status feedback, and displays results or errors without locking the page (NFR-14, NFR-18, NFR-19)
4. **Given** the status API exposes last successful refresh time/database age, **when** I view search-related status context, **then** freshness context is shown where available (FR-36)

## Tasks / Subtasks

- [x] Build search form UI in `src/mtv_dl_web/frontend/index.html`
  - [x] Add filter input controls and submit action
  - [x] Add loading and disabled states during request execution
- [x] Build result rendering flow in frontend JavaScript
  - [x] Render required metadata fields from API response
  - [x] Handle empty state and error state consistently
- [x] Integrate with current search endpoint contract (`POST /api/search`)
  - [x] Serialize filters to request payload
  - [x] Parse and present structured error messages
- [x] Add refresh/freshness context in UI status area
  - [x] Show last successful refresh time when available
  - [x] Show database age indicator when available
- [x] Add regression tests for UI search behavior
  - [x] Search while refresh is active remains responsive
  - [x] Validation and API errors are surfaced without raw internal details

## Retrospective Guardrails

- Status reconciliation: story state in this file and `sprint-status.yaml` must match before any transition.
- Evidence gate: do not mark `done` until all ACs have explicit test/verification evidence documented here.
- Dependency gate: maintain alignment with Story 1.10 refresh-trigger and freshness contract.
- Regression gate: include at least one test scenario for search + refresh concurrency behavior.

## Dev Notes

### Project Structure Notes

- Keep frontend implementation under `src/mtv_dl_web/frontend/` with vanilla HTML/CSS/JS.
- Follow existing API error display conventions and backend response formats.
- Preserve accessibility and responsive behavior for key breakpoints.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-2.3]
- [Source: _bmad-output/planning-artifacts/prd.md]
- [Source: _bmad-output/planning-artifacts/architecture.md]
- [Source: _bmad-output/implementation-artifacts/epic-1-retro-2026-05-14.md]

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- Added `tests/test_search_ui.py` first, confirmed RED state with failing assertions.
- Implemented UI updates in `src/mtv_dl_web/frontend/index.html` for loading, empty-state, freshness context, and structured search errors.
- Confirmed GREEN state for story-specific UI tests: `pytest tests/test_search_ui.py`.
- Implemented follow-up fixes for review findings: clear stale selected shows on empty results, and render URL/season/episode metadata in search results.
- Extended backend `ShowItem` mapping to expose `url`, `season`, and `episode` from search payloads.
- Re-ran UI regression tests after follow-up updates: `pytest tests/test_search_ui.py` now passing 6/6.
- Full-suite regression run (`pytest`) currently blocked by missing runtime dependency `mtv_dl` in environment (ModuleNotFoundError during collection).

### Completion Notes List

- [x] Search button now enters a disabled/loading state while `POST /api/search` runs, keeping UI interactive without page lockups.
- [x] Search results rendering keeps the results panel visible and shows a dedicated `No results` message for empty responses.
- [x] Search error handling now formats backend validation/contract errors into user-safe messages via `formatSearchError`.
- [x] Freshness context is displayed in UI via `GET /api/database/status` (`last_refresh_time` and database age indicators).
- [x] Added regression tests in `tests/test_search_ui.py` covering loading-state hooks, empty-state message, freshness area, and structured error formatter.
- [x] Search results now clear stale selections on each new render, preventing accidental downloads after empty-result searches.
- [x] Search results now display source URL and season/episode metadata where available, with safe fallbacks when metadata is absent.
- [x] Backend search response now exposes `url`, `season`, and `episode` fields for UI rendering compatibility.
- [x] Validation evidence: `pytest tests/test_search_ui.py` passed (6/6); `pytest tests/test_search.py` blocked in this environment by missing `mtv_dl` dependency.

### Change Log

- 2026-05-14: Story file scaffolded with retrospective guardrails and expanded AC coverage.
- 2026-05-14: Implemented search UI behavior updates (loading/disabled state, empty-state rendering, structured error display, freshness context) and added UI regression tests.
- 2026-05-14: Applied review follow-up fixes for selection reset and FR-4/FR-5 metadata display (`url`, `season`, `episode`) across backend and frontend.

### File List

- `src/mtv_dl_web/frontend/index.html` (modified)
- `src/mtv_dl_web/main.py` (modified)
- `tests/test_search_ui.py` (added, modified)
- `tests/test_search.py` (modified)
