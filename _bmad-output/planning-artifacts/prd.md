---
workflowType: 'prd'
workflow: 'edit'
classification:
  domain: 'self-hosted media tooling'
  projectType: 'single-user web application'
  complexity: 'moderate'
inputDocuments:
  - '/home/opencode/mtv_dl_web/spec/sw_architecture.md'
  - '/home/opencode/mtv_dl_web/spec/implementation_plan.md'
  - '/home/opencode/mtv_dl_web/spec/product_design.md'
stepsCompleted:
  - 'step-e-01-discovery'
  - 'step-e-02-review'
  - 'step-e-03-edit'
lastEdited: '2026-05-12'
editHistory:
  - date: '2026-05-08'
    changes: 'Normalized legacy PRD into BMAD structure with measurable success criteria, scope, user journeys, numbered FRs, numbered NFRs, risks, acceptance criteria, and open questions.'
  - date: '2026-05-08'
    changes: 'Resolved validation findings by clarifying scheduler auto-enqueue behavior, removing pause/resume from MVP, defining canonical database path, preserving filesystem-configured post-download hooks, tightening NFR metrics, adding web-app readiness requirements, and adding traceability.'
  - date: '2026-05-11'
    changes: 'Added FR-13 and AC-22 to address download naming patterns and folder structure requirements per GitHub issue #16. Updated traceability matrix to include new requirements.'
  - date: '2026-05-11'
    changes: 'Fixed duplicate FR-13 by renumbering to FR-14, removed duplicate AC-22, clarified AC-22 for multiple files, and updated traceability matrix accordingly.'
  - date: '2026-05-12'
    changes: 'Reviewed GitHub milestone 1 issues and added uncovered requirements for database refresh cadence/status/logging, mtv_dl dependency consolidation, and published container image workflow. Added milestone issue coverage and backlog traceability.'
  - date: '2026-05-12'
    changes: 'Clarified pyproject.toml as the single source of truth for the mtv_dl dependency version and required all imports to resolve to that exact declared version.'
  - date: '2026-05-12'
    changes: 'Cleaned planning consistency: defined APScheduler crontab syntax, aligned database path wording, added thread-safe shared-state NFR, and removed resolved cron open question.'
---

# MTV Downloader Web Interface - Product Requirements Document

## Executive Summary

The MTV Downloader Web Interface gives technically capable single users a browser-based interface for the existing `mtv_dl` CLI downloader. The product preserves existing `mtv_dl` search and download behavior while adding always-on web workflows for search, queueing, scheduling, status monitoring, configuration, and containerized deployment.

CLI-only operation is inconvenient for users who run `mtv_dl` on a home server, NAS, VPS, or local machine and want to manage downloads without opening a shell. The web interface solves this with a lightweight self-hosted web application.

The differentiator is integration-first design: the web app delegates filtering and downloading to existing `mtv_dl` behavior instead of creating a separate downloader, media manager, or duplicate database layer.

## Success Criteria

SC-1: Users can search the `mtv_dl` database from the web UI and API using filter operators `=`, `!=`, `+`, and `-`.

SC-2: Users can search with fields `description`, `region`, `size`, `channel`, `topic`, `title`, `hash`, `url`, `duration`, `age`, `start`, `dow`, `hour`, `minute`, `season`, and `episode`.

SC-3: Users can select one or more shows from search results, configure supported download options, and add downloads to the queue.

SC-4: The queue runs no more than one active download at a time and exposes `pending`, `downloading`, `completed`, and `failed` states.

SC-5: Scheduled monitoring queries automatically enqueue new non-duplicate matches and report scheduler status and errors.

SC-6: Container deployment starts with mounted configuration, data, and download volumes; a readiness check returns success; persisted files survive container restart.

SC-7: Search and download behavior matches supported `mtv_dl` CLI behavior for the documented filters and options; the web app does not bypass existing `mtv_dl` search or download logic.

SC-8: Automated tests cover search, download queueing, duplicate detection, scheduler execution, configuration loading, persistence, validation errors, and health/readiness behavior.

SC-9: The web UI remains usable in current stable desktop and mobile browsers at 360px, 768px, and 1280px viewport widths with keyboard-visible controls and status feedback.

SC-10: Users can install from a project-published container image built from the main branch and follow documentation for pulling, configuring, and running it.

## Product Scope

### MVP Scope

- Self-hosted web backend serving a static HTML/CSS/JavaScript frontend.
- Health/readiness endpoint for service and container checks.
- Search API and UI using `mtv_dl`-compatible filters.
- Result display with required metadata and series indicators where available.
- Download request API preserving existing `mtv_dl` downloader behavior.
- Single active download with pending queue support.
- Queue status display for pending, active, completed, and failed downloads.
- Queue controls for adding downloads and removing pending items.
- No pause/resume controls in MVP.
- Manual database update action.
- Automatic database refresh once every 24 hours by default, configurable through a service refresh cron expression.
- Database refresh status, last successful update time, and database age displayed where available.
- Scheduled monitoring/query execution with automatic enqueue of non-duplicate matches.
- Hash-preferred duplicate detection with URL fallback when hash is unavailable.
- User-editable service configuration file mounted outside the container image.
- Canonical container database path: `~/.mtv_dl_web/filmliste.sqlite` unless explicitly overridden by configuration.
- Container deployment with persistent mounted paths for configuration, data, post-download scripts, and downloads.
- Project-published container image built from the main branch, with documentation for where to pull it and how to run it.
- Series-aware display and file organization where supported by `mtv_dl` metadata and options.
- Post-download scripts remain configured through the filesystem and existing `mtv_dl` behavior; no web UI for hook editing is required in MVP.
- `pyproject.toml` is the single source of truth for the `mtv_dl` dependency version; vendored duplicate copies, conflicting submodule/dependency arrangements, and imports resolving to a different `mtv_dl` version are excluded from MVP.

### Future Scope

- Enhanced notifications.
- Persistent download history and scheduler execution history beyond the state needed for duplicate detection.
- Retry policies for failed scheduled jobs.
- Backup and restore for configuration and data.
- Performance monitoring dashboard.
- Multi-user support and authentication, if the product is later re-scoped beyond trusted single-user deployment.
- Queue pause/resume and active download pause/resume if downloader integration can support those controls without corrupting downloads.
- Web UI for editing post-download hook configuration.

### Out Of Scope For MVP

- Multi-user accounts.
- Authentication and authorization.
- Direct datastore querying by the web application.
- Reimplementation of `mtv_dl` filtering or downloading.
- External service dependencies.
- Frontend framework adoption.
- Multi-source downloader plugin architecture.
- Concurrent active downloads.
- Queue pause/resume controls.
- Web-based editing of post-download scripts.

## User Journeys

### Personas

- Self-hosting media archivist: Runs `mtv_dl` on a home server, NAS, VPS, or local machine and wants a browser UI for search, downloads, scheduling, and monitoring.
- Existing CLI user: Understands `mtv_dl` filters and wants queueing, scheduling, and status visibility without repeated shell commands.
- Occasional downloader: Wants to find and download shows through forms and result lists instead of remembering CLI syntax.

### Journey 1: Search And Download A Show

Applies to: self-hosting media archivist, existing CLI user, occasional downloader.

1. User opens the web UI.
2. User enters one or more `mtv_dl`-compatible filter expressions.
3. System validates filters and returns matching shows or a no-results state.
4. User selects one or more shows and chooses supported download options.
5. User adds selected shows to the queue.
6. System downloads each item when it reaches the active queue position.
7. `mtv_dl` executes its configured post-download hook script after download completion when such a script is configured; this preserves default tool behavior.
8. User sees completion or failure status for each item.

### Journey 2: Manage The Download Queue

Applies to: self-hosting media archivist, existing CLI user.

1. User opens the queue view.
2. System displays pending, active, completed, and failed items.
3. User removes pending items when needed.
4. System keeps no more than one active download.
5. User sees status updates and error messages for failed downloads.

### Journey 3: Schedule Monitoring Queries

Applies to: self-hosting media archivist, existing CLI user.

1. User creates a saved query using `mtv_dl`-compatible filters.
2. User configures an APScheduler `CronTrigger.from_crontab()` schedule.
3. Scheduler updates or checks the database at the configured interval.
4. System evaluates the saved query and identifies matching items.
5. System automatically enqueues matches whose hash, or URL fallback, is not already pending, downloading, completed, or recorded by the scheduler.
6. User reviews scheduler status, auto-enqueued items, and errors.

### Journey 4: Update The Database Manually

Applies to: self-hosting media archivist, existing CLI user.

1. User triggers a database update from the UI.
2. System starts the update through existing `mtv_dl` behavior.
3. UI shows active update status within 1 second.
4. System records refresh source, start, completion or failure, and duration in logs.
5. System reports success or failure and shows the last successful update time or database age when available.
6. Subsequent searches use the updated database.

### Journey 5: Configure The Service

Applies to: self-hosting media archivist, existing CLI user.

1. User edits the mounted configuration file for settings such as port, database path, target directories, quality, subtitles, NFO files, MKV merge, series behavior, logging, scheduler expressions, database refresh cron expression, and post-download script paths.
2. User mounts configuration, post-download scripts, data, and download directories into the container.
3. System loads configuration at startup.
4. User restarts the service when changing settings that are only loaded at startup.
5. System reports configuration validation errors before executing affected workflows.

### Journey 6: Deploy And Verify Service

Applies to: self-hosting media archivist.

1. User pulls the project-published container image or builds it locally.
2. User starts the container with mounted configuration, data, post-download script, and download paths.
3. System starts without requiring external services.
4. User runs the readiness check.
5. System reports ready status, and mounted database/configuration files remain available after restart.

## Project-Type Requirements

### Platform And Deployment

PTR-1: The product is a single-user, self-hosted web application intended for trusted local or private-network deployment.

PTR-2: The backend platform, frontend technology, and container implementation details are defined in architecture and implementation artifacts, not by product behavior.

PTR-3: Persistent runtime state shall use mounted container paths for configuration, data, post-download scripts, and downloads.

PTR-4: The application shall reuse existing `mtv_dl` behavior for search, download, database update, and post-download script execution.

PTR-15: `pyproject.toml` shall be the single source of truth for the `mtv_dl` dependency version; the application shall not keep duplicate vendored library copies, conflicting submodule copies, or alternate dependency declarations that can resolve a different version.

### Browser Support Matrix

PTR-5: The web UI shall support current stable desktop versions of Chrome, Firefox, Safari, and Edge.

PTR-6: The web UI shall support current stable mobile Safari and Chrome.

### Responsive Design

PTR-7: At 360px width, search, queue, scheduler, database update, and configuration status controls shall remain reachable without horizontal scrolling.

PTR-8: At 768px width, primary workflow controls and status content shall remain readable without overlapping controls.

PTR-9: At 1280px width or wider, search results and queue/status details shall use available horizontal space without hiding required fields.

### Accessibility

PTR-10: The web UI shall meet WCAG 2.1 AA intent for keyboard navigation, visible focus states, text contrast, labels, and status messaging.

PTR-11: Loading, completion, and failure states shall be conveyed with text, not color alone.

### Performance Targets

PTR-12: Core UI interactions shall show visible feedback within 500ms of user action, excluding long-running downloader or database update operations that expose active status.

PTR-13: Health and status requests shall respond within 500ms for 95th percentile during one active download on the target local deployment environment.

### SEO Strategy

PTR-14: Public SEO is not required for the self-hosted MVP; generated pages shall not depend on public indexing for discoverability.

## Functional Requirements

### Search

FR-1: Users can search through a web API using `mtv_dl`-compatible filter expressions.

FR-2: Users can use filter operators `=`, `!=`, `+`, and `-`.

FR-3: Users can use filter fields `description`, `region`, `size`, `channel`, `topic`, `title`, `hash`, `url`, `duration`, `age`, `start`, `dow`, `hour`, `minute`, `season`, and `episode`.

FR-4: Search results include hash, channel, title, topic, size, start, duration, age, region, URL, and downloaded state when those values exist in source data.

FR-5: Search results display season and episode when source data provides series metadata; otherwise the UI shows the item as non-series or unknown-series metadata.

### Downloads

FR-6: Users can initiate downloads from selected search results.

FR-7: Downloads preserve existing `mtv_dl` downloader behavior for supported options.

FR-8: Users can configure MVP download quality using the configured `mtv_dl` quality values exposed by the service.

FR-9: Users can configure target directories for downloads.

FR-10: Users can enable subtitle and NFO output when those options are supported by the configured `mtv_dl` installation.

FR-11: Users can enable MKV merge and file modification time behavior when those options are supported by the configured `mtv_dl` installation.

FR-12: Users can use post-download scripts configured on the filesystem and mounted into the container; MVP does not require web UI controls for editing hook scripts.

FR-13: Downloads must follow mtv_dl's naming patterns and folder structure conventions, preserving existing CLI behavior for file organization and naming.

FR-14: Completed downloads are written under the configured target directory and do not fall back to the project root or a generic `download.mp4`.

### Queue

FR-15: Users can add one or more selected shows to a download queue.

FR-16: The queue starts no more than one active download at a time.

FR-17: Users can view queue item states `pending`, `downloading`, `completed`, and `failed`.

FR-18: Users can remove pending queue items.

### Database

FR-19: The system initializes and uses the existing `mtv_dl` database integration.

FR-20: Users can trigger a manual database update action through the web interface.

FR-21: The database persists at `~/.mtv_dl_web/filmliste.sqlite` inside the container unless explicitly overridden by configuration.

FR-22: The web application shall not bypass existing `mtv_dl` database behavior to query the underlying datastore directly.

FR-34: The system shall automatically refresh the database once every 24 hours by default, with the refresh cadence configurable through a service refresh cron expression.

FR-35: The system shall start database refreshes only from a manual user action or the configured refresh schedule; search and download operations shall not implicitly trigger a refresh.

FR-36: The UI and status API shall expose the last successful database update time and database age when available from `mtv_dl` or a safe fallback.

FR-37: The system shall log database refresh start, success, failure, trigger source, and duration.

### Scheduler

FR-23: Users can create, edit, and remove scheduled monitoring queries.

FR-24: Users can configure scheduled database update and query execution with APScheduler `CronTrigger.from_crontab()` five-field syntax (`minute hour day_of_month month day_of_week`); invalid expressions are rejected before scheduling.

FR-25: Scheduled queries automatically enqueue matching items whose hash is not already pending, downloading, completed, or recorded by the scheduler; when hash is unavailable, URL is used as the duplicate key.

FR-26: Users can view scheduler job status, last run result, auto-enqueued item count, and error messages.

### Configuration

FR-27: The system loads service configuration from a user-editable configuration file mounted outside the container image.

FR-28: Configuration changes are applied on service restart unless a feature explicitly documents runtime reload behavior.

FR-29: Configuration includes port, database path, target directories, scheduler expressions, database refresh cron expression, log level, quality values, subtitle/NFO options, MKV merge behavior, file modification time behavior, series behavior, and post-download script paths.

### Deployment And UI

FR-30: The system provides container deployment artifacts, documented volume mounts, startup instructions, and readiness verification instructions.

FR-31: The system exposes a readiness endpoint for health checks.

FR-32: The system serves the web frontend without requiring a separate frontend service.

FR-33: The UI provides controls for search, download, queue, scheduler, database update, and configuration/status workflows.

FR-38: The implementation shall install and import `mtv_dl` from the exact dependency version declared in `pyproject.toml`; duplicate vendored or submodule copies shall be removed or made inactive so they cannot conflict with that declared version.

FR-39: The repository shall provide a GitHub workflow that builds and publishes a container image from the main branch, plus documentation for pulling and running that image.

## Non-Functional Requirements

NFR-1: Invalid API requests shall return a 4xx response with field-level validation information and no stack trace, verified by API tests.

NFR-2: During one active download or database update, health and status requests shall continue to respond within 500ms for 95th percentile in automated or smoke tests.

NFR-3: The API shall support at least 5 concurrent health or status requests while download execution remains limited to one active download, verified by an automated concurrency test.

NFR-4: Configuration files, database files, post-download scripts, and downloaded files shall survive container restart when mounted volumes are reused, verified by container smoke tests.

NFR-5: The MVP shall not require external services beyond local filesystem storage, the mounted `mtv_dl` database, and network access required by `mtv_dl` downloads.

NFR-6: The MVP shall assume trusted single-user deployment on localhost or a private network and shall document that public exposure is unsupported without additional controls.

NFR-7: Invalid filters, invalid schedule expressions, and invalid configured paths shall be rejected before backend execution, verified by unit or API tests.

NFR-8: Error responses shall not expose secrets, environment variable values, stack traces, or unnecessary absolute internal paths, verified by error-path tests.

NFR-9: The readiness endpoint shall return HTTP 200 with `{"status": "healthy"}` when the app is ready, verified by health tests and container smoke tests.

NFR-10: Failed downloads and scheduler jobs shall expose item/job identifier, failed state, timestamp, and human-readable error message.

NFR-11: Container smoke tests shall verify startup, readiness response, mounted path availability, and persistence after restart.

NFR-12: Configured Python formatting, type checking, frontend formatting, container linting, shell linting, and project linting checks shall pass before implementation work is considered complete.

NFR-13: At 360px, 768px, and 1280px viewport widths, all MVP controls shall remain reachable without horizontal scrolling, verified by manual or automated UI checks.

NFR-14: Long-running actions shall show a loading or active state within 1 second and a completed or failed state when execution ends.

NFR-15: Status refreshes shall not interrupt or cancel active downloads, verified by a queue/status integration test.

NFR-16: The health status indicator in the Web UI shall show three distinct states: "online" (green dot) when backend is healthy and not updating database, "updating" (yellow dot) when backend is refreshing the database, and "offline" (red dot) when backend is unhealthy or down.

NFR-17: Health check API responses shall complete within 1 second for 95th percentile to avoid UI delays.

NFR-18: The web UI and API shall remain accessible and responsive during database refresh operations, allowing users to view current status and download queue.

NFR-19: Database refresh operations shall not block or interfere with concurrent health checks, status requests, or queue management operations.

NFR-20: Shared mutable application state shall be protected from race conditions during concurrent requests, background downloads, and database refresh operations, verified by concurrency tests.

## Risks And Mitigations

| Risk | Mitigation |
| --- | --- |
| Existing `mtv_dl` CLI assumptions may not map cleanly to API usage. | Preserve existing `mtv_dl` behavior and cover integration behavior with tests. |
| Active download pause/resume may not be feasible without deeper process control. | Exclude pause/resume controls from MVP; keep them in Future Scope. |
| "All CLI functionality" is too broad without explicit option mapping. | Track MVP parity through explicit configuration options in FR-29 and future stories. |
| Scheduler duplicate detection depends on stable identifiers. | Use hash as the primary duplicate key and URL fallback when hash is unavailable. |
| Auto-enqueue may queue unwanted matches if saved filters are broad. | Show scheduler status, auto-enqueued counts, and queue items so users can remove pending items before download starts. |
| Container path ambiguity can cause persistence bugs. | Use `~/.mtv_dl_web/filmliste.sqlite` as canonical database path unless configuration overrides it. |
| No-auth single-user deployment is unsafe on public networks. | Document trusted-network deployment assumptions and keep authentication out of MVP scope. |
| Direct datastore access would duplicate `mtv_dl` logic and create behavior drift. | Enforce existing `mtv_dl` integration usage in architecture, code review, and tests. |
| Conflicting `mtv_dl` dependency sources could make behavior depend on import path order. | Use `pyproject.toml` as the single version source and test that local, test, and container imports resolve to that declared dependency version. |
| Published container images could drift from documented runtime configuration. | Build images from main branch through CI and keep pull/run documentation in the same delivery story. |

## Acceptance Criteria

AC-1: Given a populated `mtv_dl` database, when the user submits supported filters through the UI or API, then matching results return required metadata for available fields.

AC-2: Given an invalid filter field, operator, schedule expression, or configured path, when the user submits it, then the system rejects it before backend execution and returns a validation error.

AC-3: Given multiple selected shows, when the user adds them to the queue, then the system records pending items and starts no more than one active download.

AC-4: Given an active or completed queue, when the user opens the queue view, then each item shows one supported state and any failure message.

AC-5: Given a pending queue item, when the user removes it, then it no longer appears in the queue and is not downloaded.

AC-6: Given a configured manual database update action, when the user triggers it, then the system reports active, success, or failure status and subsequent searches use the updated database.

AC-7: Given a scheduled query and valid APScheduler `CronTrigger.from_crontab()` expression, when the schedule fires, then the system evaluates the query and automatically enqueues new matches that are not duplicates by hash or URL fallback.

AC-8: Given a duplicate scheduled match, when the item hash or URL fallback already exists in pending, downloading, completed, or scheduler-recorded state, then the item is not enqueued again.

AC-9: Given mounted configuration, data, post-download scripts, and download volumes, when the container restarts, then configuration, database, scripts, and downloaded files remain available.

AC-10: Given a running container, when the readiness endpoint is requested, then it returns HTTP 200 and `{"status": "healthy"}`.

AC-11: Given supported download options, when the user starts a download, then the backend passes those options through existing `mtv_dl` behavior in the expected format.

AC-12: Given post-download scripts configured on the filesystem and mounted into the container, when `mtv_dl` invokes configured hooks, then the web app does not block or replace that behavior.

AC-13: Given viewport widths of 360px, 768px, and 1280px, when the user opens the UI, then search, queue, scheduler, database update, and configuration/status controls remain reachable without horizontal scrolling.

AC-14: Given one active download, when five concurrent health or status requests are made, then requests complete successfully within the defined performance target.

AC-15: Given the Web UI health status indicator, when the backend is healthy and not updating database, then it shows "online" with green dot.

AC-16: Given the Web UI health status indicator, when the backend is refreshing the database, then it shows "updating" with yellow dot.

AC-17: Given the Web UI health status indicator, when the backend is unhealthy or down, then it shows "offline" with red dot.

AC-18: Given a health check request, when executed, then it completes within 1 second for 95th percentile.

AC-19: Given a database refresh operation is in progress, when a user accesses the web UI, then the UI remains accessible and shows current status and download queue.

AC-20: Given a database refresh operation is in progress, when health check or status API requests are made, then they complete successfully within performance targets.

AC-21: Given a database refresh operation is in progress, when queue management operations are performed, then they execute normally without being blocked by the refresh operation.

AC-22: Given a completed download, when the system verifies the files, then all file names match the configured naming pattern and files are located in the configured target directory.

AC-23: Given default configuration, when the service runs continuously, then database refresh is scheduled once every 24 hours unless the user configures a different refresh cron expression through the configuration file or environment.

AC-24: Given a user performs search or download operations, when no manual or scheduled refresh is active, then those operations do not start a database refresh.

AC-25: Given a database refresh runs, when it starts and completes or fails, then the UI/status API expose current or last update state and the logs record trigger source, outcome, and duration.

AC-26: Given a clean checkout, when dependencies are installed and the app imports `mtv_dl`, then the import resolves to the exact dependency version declared in `pyproject.toml` and duplicate vendored/submodule copies are absent or inactive.

AC-27: Given a successful main-branch CI run, when a user follows the container documentation, then they can pull the published image and run it with the documented mounted configuration, data, and download paths.

## Traceability Matrix

| Success Criterion | Journeys | Related FRs | Related ACs |
| --- | --- | --- | --- |
| SC-1 | Journey 1, Journey 3 | FR-1, FR-2 | AC-1, AC-2 |
| SC-2 | Journey 1, Journey 3 | FR-3, FR-4, FR-5 | AC-1 |
| SC-3 | Journey 1, Journey 5 | FR-6 through FR-14, FR-29 | AC-3, AC-11, AC-12, AC-22 |
| SC-4 | Journey 2 | FR-15 through FR-18 | AC-3, AC-4, AC-5 |
| SC-5 | Journey 3 | FR-23 through FR-26 | AC-7, AC-8 |
| SC-6 | Journey 6 | FR-21, FR-27 through FR-32, FR-39, NFR-4, NFR-9, NFR-11, NFR-16, NFR-17, NFR-18, NFR-19 | AC-9, AC-10, AC-15, AC-16, AC-17, AC-18, AC-19, AC-20, AC-21, AC-27 |
| SC-7 | Journey 1, Journey 3, Journey 4 | FR-7, FR-19, FR-20, FR-22, FR-34 through FR-38 | AC-1, AC-6, AC-11, AC-23, AC-24, AC-25, AC-26 |
| SC-8 | All journeys | NFR-1 through NFR-20 | AC-1 through AC-27 |
| SC-9 | Journey 1 through Journey 6 | PTR-5 through PTR-14, FR-33, NFR-13 | AC-13 |
| SC-10 | Journey 6 | FR-30, FR-39 | AC-27 |

## Milestone 1 Issue Coverage

Reviewed from GitHub milestone 1, "MVP: search and download", on 2026-05-12.

| Issue | Coverage Decision |
| --- | --- |
| #1 Health status not working | Covered by NFR-16, NFR-17, AC-15 through AC-18, and backlog Story 1.5. No new requirement added. |
| #7 Add workflow to create containers | Added FR-39, AC-27, SC-10, and backlog Story 1.12. |
| #9 Can't access web UI while refreshing the database | Covered by NFR-18, NFR-19, AC-19 through AC-21, and backlog Story 1.6. No new requirement added. |
| #10 Log output should show database updates | Added FR-37, AC-25, and backlog Story 1.10. |
| #12 Revisit integration of mtv_dl binaries | Added PTR-15, FR-38, AC-26, and backlog Story 1.11. |
| #16 Download ends up in root folder with download.mp4 | Covered by FR-13, FR-14, AC-22, and backlog Story 1.13. No new requirement added. |
| #17 Tests report warnings | Covered by NFR-12 and existing implementation quality gate. Closed issue; no new requirement added. |
| #21 Improve database refreshes | Added FR-34 through FR-36, AC-23 through AC-25, and backlog Story 1.10. |
| #24 Tests are broken | Covered by NFR-12 and existing implementation quality gate. Closed issue; no new requirement added. |

## Delivery Notes

Detailed implementation sequencing belongs in `spec/implementation_plan.md`. Architecture choices, framework versions, concrete imports, linter names, and script names belong in architecture, implementation, and engineering standards artifacts.

The PRD defines product scope and acceptance expectations. Implementation planning should align stories to the numbered requirements and traceability matrix in this document.

## Open Questions

OQ-1: Which remaining CLI options, beyond quality, target directory, subtitles, NFO, MKV merge, file modification time, series behavior, and post-download script paths, are required for MVP parity?
