---
title: 'GH-78 Align Web Search With mtv_dl dump'
type: 'bugfix'
created: '2026-05-15T00:00:00Z'
status: 'done'
baseline_commit: 'b87dc3703374f332ed2f87dc686afb87f75f71c5'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The web search endpoint returns far fewer matches than `mtv_dl dump` for the same filters (example: `title=tagesschau`), which breaks trust in the UI and makes the web app look functionally incorrect. Today, the web implementation does not execute the same refresh-and-query path that `mtv_dl dump` uses.

**Approach:** Change web search to use the same mtv_dl query/filter logic as `mtv_dl dump` while enforcing a strict no-update policy in the web request path, then add regression coverage that proves parity is achieved without triggering any database update during search.

## Boundaries & Constraints

**Always:** Keep scope limited to issue #78 search-parity bug; preserve existing API contract for `POST /api/search`; use mtv_dl primitives rather than custom SQL; keep error responses structured with safe HTTP errors; update tests to cover parity-critical behavior; and never trigger any database update/refresh from `/api/search`.

**Ask First:** If strict no-update search behavior requires changing existing docs or operational defaults beyond issue #78 scope, halt and ask before expanding scope.

**Never:** Do not refactor unrelated queue/download/UI styling flows; do not add new endpoints; do not introduce a second independent search engine; do not pin logic to hardcoded one-off filters like `tagesschau`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Search parity happy path | `POST /api/search` with filters such as `title=tagesschau`, mtv_dl DB available | Search results are produced through the same mtv_dl query path used by `mtv_dl dump`, eliminating large-count divergence caused by the previous web-only path | N/A |
| Stale DB refresh window | Search request arrives when DB is older than mtv_dl refresh threshold | Web search still executes without triggering any DB refresh/update and returns results from currently available DB state | If DB is unusable, return structured 5xx error without raw traceback leakage |
| Missing/corrupt DB files | Search request with valid filters, but filmlist/history DB unavailable or unreadable | Endpoint fails predictably with structured error contract | Return HTTP error with actionable detail, log root exception server-side |
| Invalid filters | Malformed/unsupported filter fields/operators | Request is rejected before running search query | Return 400 with validation detail |

</frozen-after-approval>

## Code Map

- `src/mtv_dl_web/main.py` -- current search endpoint and DB connection lifecycle; primary bugfix location
- `src/mtv_dl_web/config/settings.py` -- current database path contract; may need alignment rules for mtv_dl-compatible DB usage
- `tests/test_search.py` -- API-level regression tests for search behavior and error handling
- `README.md` -- user-facing configuration semantics for DB path/refresh behavior if behavior contract changes

## Tasks & Acceptance

**Execution:**
- [x] `src/mtv_dl_web/main.py` -- route `/api/search` through shared mtv_dl filter/query logic while explicitly disabling any refresh/update trigger in the request path -- removes root parity mismatch without mutating DB on search
- [x] `src/mtv_dl_web/main.py` -- align DB file resolution and database object construction with mtv_dl dump-compatible expectations (including filmlist/history pairing) while preserving no-update behavior -- ensures both entrypoints read equivalent data sources
- [x] `tests/test_search.py` -- add/adjust tests asserting search execution uses the dump-equivalent mtv_dl path and maintains structured failure behavior -- prevents regressions for issue #78
- [x] `README.md` -- update documentation if DB path or refresh semantics change from current text -- avoids operator confusion after parity fix

**Acceptance Criteria:**
- Given equivalent filter input and the same mtv_dl data directory, when the web endpoint and `mtv_dl dump` are run against that data, then result sets are derived from the same mtv_dl query lifecycle rather than divergent web-only behavior.
- Given the filmlist is older than the mtv_dl refresh threshold, when `/api/search` executes, then no database update/refresh is triggered and the query runs against the current local DB state.
- Given valid filters and healthy DB files, when `/api/search` succeeds, then it still returns the existing response schema (`results` with show fields) and remains compatible with current UI rendering.
- Given invalid filters or backend failures, when `/api/search` fails, then the API returns structured 4xx/5xx errors without exposing internal traceback content.

## Spec Change Log

## Design Notes

- Favor a single search execution helper that is explicitly parity-oriented with `mtv_dl dump`, so parity is implemented once and reused by the endpoint.
- Keep conversion from mtv_dl row data to `ShowItem` isolated after query execution so parity logic and response-shaping logic remain separable and testable.

## Verification

**Commands:**
- `pytest tests/test_search.py` -- expected: all search tests pass including new parity-focused coverage
- `pytest` -- expected: full suite passes with no regressions in existing search/download/queue behavior

## Suggested Review Order

**Search parity database path**

- Start here: mtv_dl-compatible filenames with legacy-safe fallback for existing installs.
  [`main.py:304`](../../src/mtv_dl_web/main.py#L304)

- Keep imports dependency-safe across mtv_dl versions while preserving Database/Downloader integration.
  [`main.py:32`](../../src/mtv_dl_web/main.py#L32)

**No-refresh request behavior proof**

- Verify `/api/search` still uses explicit no-refresh connection flags.
  [`test_search.py:183`](../../tests/test_search.py#L183)

- Confirm directory-path filename expectations match runtime selection rules.
  [`test_search.py:204`](../../tests/test_search.py#L204)

**Operator-facing contract update**

- Check documentation now reflects mtv_dl default filename semantics for directory paths.
  [`README.md:180`](../../README.md#L180)
