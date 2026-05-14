# Story 2.3: Build Search UI

Status: ready-for-dev

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

- [ ] Build search form UI in `src/mtv_dl_web/frontend/index.html`
  - [ ] Add filter input controls and submit action
  - [ ] Add loading and disabled states during request execution
- [ ] Build result rendering flow in frontend JavaScript
  - [ ] Render required metadata fields from API response
  - [ ] Handle empty state and error state consistently
- [ ] Integrate with current search endpoint contract (`POST /api/search`)
  - [ ] Serialize filters to request payload
  - [ ] Parse and present structured error messages
- [ ] Add refresh/freshness context in UI status area
  - [ ] Show last successful refresh time when available
  - [ ] Show database age indicator when available
- [ ] Add regression tests for UI search behavior
  - [ ] Search while refresh is active remains responsive
  - [ ] Validation and API errors are surfaced without raw internal details

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

TBD

### Debug Log References

TBD

### Completion Notes List

- [ ] TBD

### Change Log

- 2026-05-14: Story file scaffolded with retrospective guardrails and expanded AC coverage.

### File List

- `src/mtv_dl_web/frontend/index.html` (planned)
- `src/mtv_dl_web/frontend/*.js` (planned)
- `tests/*` (planned)
