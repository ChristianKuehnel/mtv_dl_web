---
title: 'Issue 54: Add refresh database button to web UI'
type: 'bugfix'
created: '2026-05-14T00:00:00Z'
status: 'done'
baseline_commit: '5b6c4778bf77a4ea4506c07fb08a330ac10b7114'
context:
  - '{project-root}/_bmad-output/project-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Issue #54 reports a missing user control: the web UI does not expose a way to trigger database refresh, even though the backend already supports manual refresh. This leaves users unable to recover stale search data from the interface and forces non-UI workarounds.

**Approach:** Add a dedicated "Refresh Database" button in the existing UI header area, connect it to the existing `POST /api/database/refresh` endpoint, and keep button state synchronized with refresh activity using `GET /api/database/status`. Preserve all existing search/download behavior while adding clear user feedback for started, in-progress, completed, and failed refresh requests.

## Boundaries & Constraints

**Always:** Reuse the existing backend API routes (`POST /api/database/refresh`, `GET /api/database/status`) rather than introducing new refresh endpoints; keep UI behavior aligned with current status messaging patterns (`showStatus`); disable refresh control while backend reports `is_refreshing=true`; preserve existing page structure and Tailwind-based visual language; keep implementation scoped to a single user-facing goal from issue #54.

**Ask First:** Any request to change API contract semantics (for example switching "already in progress" from 200/message to 409/error), add authentication/authorization requirements, or redesign the page layout beyond a small incremental control addition.

**Never:** Do not reimplement refresh logic in frontend or bypass backend state checks; do not alter download/search workflows unrelated to refresh; do not introduce new persistence, schedulers, or background worker systems for this issue; do not silently hide refresh failures.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Trigger manual refresh | User clicks Refresh button while `is_refreshing=false` and backend reachable | Frontend sends `POST /api/database/refresh`; status bar confirms refresh start; button transitions to disabled "refreshing" state on next status poll | If response not OK, show error and keep/revert button enabled |
| Duplicate click during active refresh | User clicks while backend reports `is_refreshing=true` | No duplicate user-perceived action; button remains disabled; status indicates refresh already in progress | If stale client state allowed click, backend response message is shown and UI returns to disabled state after status refresh |
| Refresh completion | Polling observes transition `is_refreshing: true -> false` | Button becomes enabled again; optional informational status indicates refresh is complete and UI is ready for search | If status payload missing fields, fail safe by enabling button and showing non-blocking error |
| Backend/API failure | Network error, timeout, or server failure on refresh request/status poll | User sees actionable error message in status bar; existing search/download controls stay usable | Log to console for debugging and avoid leaving button stuck disabled |

</frozen-after-approval>

## Code Map

- `src/mtv_dl_web/frontend/index.html` -- Main SPA markup and inline JavaScript where new refresh button UI, API call wiring, and refresh-state polling integration will be added.
- `src/mtv_dl_web/main.py` -- Existing refresh/status endpoints; verify response behavior is sufficient for UI wiring and adjust only if needed for consistent client handling.
- `tests/test_database_refresh.py` -- Backend tests for manual refresh/status endpoint behavior; extend assertions to support the UI-facing contract used by this change.

## Tasks & Acceptance

**Execution:**
- [x] `src/mtv_dl_web/frontend/index.html` -- Add a "Refresh Database" button in the header/status control area and define accessible default/disabled visual states -- makes the feature discoverable in the UI.
- [x] `src/mtv_dl_web/frontend/index.html` -- Implement `triggerDatabaseRefresh` and `refreshDatabaseStatus` client functions, wire button click handler, and coordinate with existing polling lifecycle -- connects user action to API and keeps control state accurate.
- [x] `src/mtv_dl_web/frontend/index.html` -- Integrate user feedback into existing `showStatus` flow for start/already-running/completed/error outcomes without regressing current notifications -- provides clear operational feedback.
- [x] `src/mtv_dl_web/main.py` -- Confirm refresh endpoint response shape/messages consumed by the UI and make only minimal compatibility adjustments if required -- stabilizes contract for frontend behavior.
- [x] `tests/test_database_refresh.py` -- Strengthen manual refresh/status tests (including "already in progress" branch via mocks) to assert the API behaviors the UI relies on -- prevents regressions in button workflow.

**Acceptance Criteria:**
- Given the web UI is loaded and backend is healthy, when the user clicks `Refresh Database`, then the frontend sends `POST /api/database/refresh` and displays a success-style status message indicating refresh was started.
- Given a refresh is already running, when the page evaluates refresh status, then the refresh button is disabled and cannot trigger concurrent manual refresh from normal interaction.
- Given backend reports refresh is in progress, when status polling updates the UI, then the refresh control communicates a refreshing state and remains disabled until refresh completes.
- Given refresh state changes from in-progress to idle, when the next status poll succeeds, then the refresh button is re-enabled without requiring page reload.
- Given the refresh request fails due to network/server error, when the user attempts manual refresh, then the UI shows an error message and preserves usability of search and download controls.
- Given existing search/download functionality is used before and after refresh actions, when users perform those flows, then no regression is introduced by the refresh-button changes.

## Spec Change Log

## Design Notes

The backend already exposes both a trigger endpoint and a status endpoint, so the safest design is thin UI orchestration: initiate refresh explicitly, then trust polled backend state as the source of truth for button availability. This avoids race-prone client-only timers and aligns with the current architecture where health/download views are also poll-driven.

A practical interaction pattern here is:

```js
await triggerDatabaseRefresh();
await refreshDatabaseStatus();
setInterval(refreshDatabaseStatus, 5000);
```

The button text and disabled state should be derived from latest `is_refreshing` data, not only from immediate click results, so the UI recovers correctly after transient failures or delayed refresh starts.

## Verification

**Commands:**
- `pytest tests/test_database_refresh.py` -- expected: all refresh-related endpoint tests pass with updated assertions.
- `pytest` -- expected: full suite passes with no regressions.

## Suggested Review Order

**UI entry point and control placement**

- Starts the feature with visible, discoverable refresh control in header.
  [`index.html:31`](../../src/mtv_dl_web/frontend/index.html#L31)

- Wires user click into the refresh action path.
  [`index.html:664`](../../src/mtv_dl_web/frontend/index.html#L664)

**Refresh-state orchestration and resilience**

- Centralizes button disabled/text/icon state for consistency.
  [`index.html:272`](../../src/mtv_dl_web/frontend/index.html#L272)

- Polls backend status with payload validation and transition handling.
  [`index.html:282`](../../src/mtv_dl_web/frontend/index.html#L282)

- Handles manual trigger robustly for JSON and non-JSON responses.
  [`index.html:324`](../../src/mtv_dl_web/frontend/index.html#L324)

- Initializes refresh polling with existing health/download polling lifecycle.
  [`index.html:667`](../../src/mtv_dl_web/frontend/index.html#L667)

**Backend contract coverage tests**

- Verifies status payload fields required by the UI.
  [`test_database_refresh.py:71`](../../tests/test_database_refresh.py#L71)

- Verifies manual refresh success branch response contract.
  [`test_database_refresh.py:91`](../../tests/test_database_refresh.py#L91)

- Verifies already-in-progress and failed-start response branches.
  [`test_database_refresh.py:104`](../../tests/test_database_refresh.py#L104)
