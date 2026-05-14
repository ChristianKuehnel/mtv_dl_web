# Story 3.4: Build Queue UI

Status: ready-for-dev

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

- [ ] Extend queue UI in `src/mtv_dl_web/frontend/index.html`
  - [ ] Add queue section with grouped or labeled item states
  - [ ] Add per-item remove action for pending entries only
- [ ] Extend frontend JS queue client logic
  - [ ] Poll `GET /queue` and render live states
  - [ ] Call `DELETE /queue/{id}` and refresh UI state
  - [ ] Reuse existing status banner patterns for success/errors
- [ ] Preserve accessibility and responsiveness
  - [ ] Keyboard reachable controls with visible state text
  - [ ] Layout validation at 360px, 768px, 1280px
- [ ] Add tests/manual verification notes
  - [ ] UI behavior check for each state
  - [ ] Remove action only available for pending entries

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

TBD

### Debug Log References

TBD

### Completion Notes List

- [ ] Ultimate context engine analysis completed - comprehensive developer guide created

### File List

- `src/mtv_dl_web/frontend/index.html` (planned)
- `tests/` (planned)
