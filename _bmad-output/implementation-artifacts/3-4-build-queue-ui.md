# Story 3.4: Build Queue UI

Status: done

## Story

As a user,
I want to view and manage the queue in the UI,
So that I can monitor download status.

## Acceptance Criteria

1. **Given** the queue page, **when** I view it, **then** it shows `pending`, `downloading`, `completed`, and `failed` items (FR-17).
2. **Given** a pending item, **when** I click "Remove", **then** it disappears from the queue (FR-18).
3. **Given** long-running queue actions, **when** items are added/removed, **then** loading/active status is shown within 1 second (NFR-14).
4. **Given** mobile and desktop breakpoints, **when** I access queue controls, **then** controls remain reachable and readable (NFR-13).

## Tasks / Subtasks

- [x] Extend queue UI in `src/mtv_dl_web/frontend/index.html`
  - [x] Add queue section with grouped or labeled item states
  - [x] Add per-item remove action for pending entries only
- [x] Extend frontend JS queue client logic
  - [x] Poll `GET /queue` and render live states
  - [x] Call `DELETE /queue/{id}` and refresh UI state
  - [x] Reuse existing status banner patterns for success/errors
- [x] Preserve accessibility and responsiveness
  - [x] Keyboard reachable controls with visible state text
  - [x] Layout validation at 360px, 768px, 1280px
- [x] Add tests/manual verification notes
  - [x] UI behavior check for each state
  - [x] Remove action only available for pending entries

## Retrospective Guardrails

- UX gate: state should be communicated with text, not color alone.
- Regression gate: existing search and download workflows in `index.html` must keep working.
- Contract gate: frontend queue calls must match backend queue API payload and response fields exactly.

## Dev Notes

### Current State and Required Change

- Current UI in `src/mtv_dl_web/frontend/index.html` shows search and active download status, but no queue-management view with pending/completed/failed states.
- Add queue-specific rendering and controls without introducing frontend frameworks.
- Keep API base (`/api`) and existing fetch/style patterns consistent.

### What Must Be Preserved

- Existing health indicator behavior (`online`, `updating`, `offline`).
- Existing search parsing and result rendering behavior.
- Existing download option controls and submit flow.

### Architecture and Compliance Requirements

- Frontend remains static vanilla HTML/CSS/JS in `src/mtv_dl_web/frontend/`.
- No frontend build pipeline introduction.
- Continue structured error display and non-blocking UI updates.

### Testing Requirements

- Add or update tests that verify queue state rendering and remove action behavior.
- Validate no horizontal overflow for primary controls at required breakpoints.
- Confirm loading/feedback state appears promptly on queue operations.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-3.4-Build-Queue-UI]
- [Source: _bmad-output/planning-artifacts/prd.md#Queue]
- [Source: _bmad-output/planning-artifacts/prd.md#NFR-13]
- [Source: _bmad-output/planning-artifacts/prd.md#NFR-14]
- [Source: src/mtv_dl_web/frontend/index.html]

## Dev Agent Record

### Agent Model Used

openai/gpt-5.3-codex

### Debug Log References

- `pytest tests/test_search_ui.py`

### Completion Notes List

- [x] Added queue UI section with explicit state text and pending-only remove controls.
- [x] Added queue polling (`1s`) and remove action with success/error status banner updates.
- [x] Added UI contract tests validating queue state/remove semantics and feedback interval.

### File List

- `src/mtv_dl_web/frontend/index.html`
- `tests/test_search_ui.py`

## Change Log

- 2026-05-14: Added queue management UI and polling/remove client behavior with regression coverage.
