---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories']
inputDocuments: ['_bmad-output/planning-artifacts/prd.md', '_bmad-output/planning-artifacts/architecture.md']
---

# mtv_dl_web - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for **mtv_dl_web**, decomposing the requirements from the PRD and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

**Search (FR-1 to FR-5)**:
- FR-1: Web API for `mtv_dl`-compatible filter expressions.
- FR-2: Support filter operators `=`, `!=`, `+`, `-`.
- FR-3: Support filter fields (`description`, `region`, `size`, `channel`, `topic`, `title`, `hash`, `url`, `duration`, `age`, `start`, `dow`, `hour`, `minute`, `season`, `episode`).
- FR-4: Search results include hash, channel, title, topic, size, start, duration, age, region, URL, and downloaded state.
- FR-5: Display season/episode metadata where available.

**Downloads (FR-6 to FR-14)**:
- FR-6: Initiate downloads from search results.
- FR-7: Preserve `mtv_dl` downloader behavior.
- FR-8: Configure download quality.
- FR-9: Configure target directories.
- FR-10: Enable subtitles/NFO output.
- FR-11: Enable MKV merge and file modification time behavior.
- FR-12: Support post-download scripts (filesystem-configured).
- FR-13: Preserve `mtv_dl` naming patterns and folder structure conventions.
- FR-14: Verify completed downloads are named following the patterns configured for mtv_dl and stored under the configured target directory.

**Queue (FR-15 to FR-18)**:
- FR-15: Add selected shows to download queue.
- FR-16: Single active download at a time.
- FR-17: View queue states (`pending`, `downloading`, `completed`, `failed`).
- FR-18: Remove pending queue items.

**Database (FR-19 to FR-22, FR-34 to FR-37)**:
- FR-19: Reuse `mtv_dl` database integration.
- FR-20: Manual database update action.
- FR-21: Persist database at `~/.mtv_dl_web/filmliste.sqlite`.
- FR-22: No direct datastore querying.
- FR-34: Automatic database refresh every 24 hours by default, configurable.
- FR-35: Database refreshes start only from manual action or schedule, not search/download operations.
- FR-36: UI/status API exposes last successful database update time and database age when available.
- FR-37: Log database refresh start, success, failure, trigger source, and duration.

**Scheduler (FR-23 to FR-26)**:
- FR-23: Create/edit/remove scheduled monitoring queries.
- FR-24: Configure cron-like schedules.
- FR-25: Auto-enqueue non-duplicate matches (hash/URL fallback).
- FR-26: View scheduler status, auto-enqueued items, and errors.

**Configuration (FR-27 to FR-29, FR-38)**:
- FR-27: Load configuration from mounted file.
- FR-28: Apply config changes on restart.
- FR-29: Configure port, database path, target directories, scheduler, database refresh interval, log level, quality, subtitles/NFO, MKV merge, series behavior, and post-download scripts.
- FR-38: Use a single canonical `mtv_dl` dependency source; remove duplicate vendored/submodule sources.

**Deployment/UI (FR-30 to FR-33, FR-39)**:
- FR-30: Container deployment with mounted volumes.
- FR-31: Readiness endpoint for health checks.
- FR-32: Serve static frontend.
- FR-33: UI controls for search, download, queue, scheduler, database update, and configuration.
- FR-39: Publish a main-branch container image through GitHub workflow and document how to pull/run it.

### NonFunctional Requirements

**Performance (NFR-2, NFR-3)**:
- NFR-2: Health/status requests respond within 500ms (95th percentile).
- NFR-3: Support 5+ concurrent health/status requests.

**Persistence (NFR-4)**:
- NFR-4: Mounted volumes survive container restart.

**Security (NFR-6, NFR-8)**:
- NFR-6: No external services (trusted single-user deployment).
- NFR-8: Error responses do not expose secrets/stack traces.

**Validation (NFR-7)**:
- NFR-7: Reject invalid filters/schedules/paths before execution.

**UI/UX (NFR-13, NFR-14)**:
- NFR-13: Responsive design (360px, 768px, 1280px).
- NFR-14: Loading states within 1 second.

### Additional Requirements

**Starter Template**:
- Use existing repository + `uv sync` for dependencies.
- No frontend build pipeline (vanilla JS/CSS).

**API Design**:
- Minimalist REST endpoints (`/search`, `/queue`, `/downloads`).
- Structured error responses (`{ error: { code, message } }`).

**Project Structure**:
- Backend: `src/main.py` (FastAPI).
- Frontend: `src/frontend/js/` (vanilla JS modules).
- Tests: `tests/` (separate from source).

**Integration**:
- Reuse `mtv_dl.Database` and `mtv_dl.Downloader` from the canonical dependency source selected by the project.
- Do not keep duplicate vendored/submodule copies that can conflict with the selected dependency path.

### UX Design Requirements

None (UI requirements covered by PRD).

### FR Coverage Map

| FR/NFR | Epic | Description                          |
|--------|------|--------------------------------------|
| FR-1   | 2    | Search API                           |
| FR-2   | 2    | Filter operators                     |
| FR-3   | 2    | Filter fields                        |
| FR-4   | 2    | Search results metadata              |
| FR-5   | 2    | Season/episode display               |
| FR-6   | 3    | Download initiation                  |
| FR-7   | 3    | Preserve `mtv_dl` behavior           |
| FR-8   | 3    | Download quality configuration       |
| FR-9   | 3    | Target directory configuration       |
| FR-10  | 3    | Subtitles/NFO output                 |
| FR-11  | 3    | MKV merge behavior                   |
| FR-12  | 3    | Post-download scripts                |
| FR-13  | 1    | Download naming/folder behavior      |
| FR-14  | 1    | Download target verification         |
| FR-15  | 3    | Add to queue                         |
| FR-16  | 3    | Single active download               |
| FR-17  | 3    | View queue states                    |
| FR-18  | 3    | Remove pending items                 |
| FR-19  | 1    | Reuse `mtv_dl` database              |
| FR-20  | 1    | Manual database update               |
| FR-21  | 1    | Database persistence                 |
| FR-22  | 1    | No direct datastore querying         |
| FR-23  | 4    | Create/edit scheduled queries        |
| FR-24  | 4    | Cron-like schedules                  |
| FR-25  | 4    | Auto-enqueue non-duplicates          |
| FR-26  | 4    | View scheduler status                |
| FR-27  | 1    | Load configuration                    |
| FR-28  | 1    | Apply config changes on restart      |
| FR-29  | 1    | Configure service settings           |
| FR-30  | 1    | Container deployment                 |
| FR-31  | 1    | Readiness endpoint                   |
| FR-32  | 1    | Serve static frontend                |
| FR-33  | 5    | UI controls                          |
| FR-34  | 1    | Automatic database refresh cadence   |
| FR-35  | 1    | Refresh trigger boundaries           |
| FR-36  | 1    | Database update timestamp/age status |
| FR-37  | 1    | Database refresh logging             |
| FR-38  | 1    | Canonical mtv_dl dependency source   |
| FR-39  | 1    | Published container image workflow   |
| NFR-13 | 5    | Responsive design                    |
| NFR-14 | 5    | Loading states                       |
| NFR-16 | 1    | Health status indicator              |
| NFR-17 | 1    | Health check performance             |
| NFR-18 | 1    | Concurrent web UI access             |
| NFR-19 | 1    | Non-blocking database operations     |
| NFR-20 | 1    | Thread-safe shared state operations  |

## Epic List

### Epic 1: Project Foundation & Configuration

**Goal**: Users can deploy and configure the service with persistent storage.

### Story 1.1: Initialize FastAPI Backend

As a self-hosting user,
I want a FastAPI backend with basic project structure,
So that I can extend it for search, queue, and scheduler functionality.

**Acceptance Criteria:**

**Given** the existing repository,
**When** I run `uv sync`,
**Then** dependencies are installed successfully.

**Given** `src/main.py`,
**When** I start the FastAPI app,
**Then** it runs without errors on the configured port.

**Given** the project structure,
**When** I inspect `src/`,
**Then** it matches the architecture (`main.py`, `config.py`, `frontend/`, `mtv_dl/`).

---

### Story 1.2: Implement Readiness Endpoint

As a self-hosting user,
I want a readiness endpoint (`/health`),
So that I can verify the service is running and healthy.

**Acceptance Criteria:**

**Given** a running service,
**When** I call `GET /health`,
**Then** it returns `200 OK` with `{ "status": "healthy" }`.

**Given** the endpoint,
**When** I check the response time,
**Then** it responds within 500ms (NFR-2).

---

### Story 1.3: Configure Mounted Volumes (Docker)

As a self-hosting user,
I want mounted volumes for configuration, data, and downloads,
So that my files persist after container restarts.

**Acceptance Criteria:**

**Given** a `Dockerfile` and `docker-compose.yml`,
**When** I start the container with mounted volumes,
**Then** files in `/data`, `/downloads`, and `/config` persist after restart (NFR-4).

**Given** the container,
**When** I inspect mounted paths,
**Then** they match the architecture (`~/.mtv_dl_web/filmliste.sqlite` for database).

---

### Story 1.4: Load Service Configuration

As a self-hosting user,
I want to configure service settings via a mounted file,
So that I can customize port, database path, and download options.

**Acceptance Criteria:**

**Given** a configuration file (e.g., `config.yaml`),
**When** I start the service,
**Then** it loads settings (port, database path, target directories) from the file (FR-27, FR-28).

**Given** invalid configuration,
**When** I start the service,
**Then** it rejects the config and logs an error (NFR-7).

---

### Story 1.5: Improve Health Status Monitoring

As a self-hosting user,
I want the Web UI to show accurate health status with three states (online/updating/offline),
So that I can quickly understand the backend status and database update state.

**Acceptance Criteria:**

**Given** a healthy backend not updating database,
**When** I view the Web UI health status indicator,
**Then** it shows "online" with a green dot (NFR-16, AC-15).

**Given** a backend that is refreshing the database,
**When** I view the Web UI health status indicator,
**Then** it shows "updating" with a yellow dot (NFR-16, AC-16).

**Given** an unhealthy or down backend,
**When** I view the Web UI health status indicator,
**Then** it shows "offline" with a red dot (NFR-16, AC-17).

**Given** a health check request,
**When** executed,
**Then** it completes within 1 second for 95th percentile (NFR-17, AC-18).

---

### Story 1.6: Enable Concurrent Web UI Access During Database Refresh

As a self-hosting user,
I want to access the web UI and perform status/queue operations while the database is refreshing,
So that I can monitor the system and manage downloads without interruption.

**Acceptance Criteria:**

**Given** a database refresh operation is in progress,
**When** I access the web UI,
**Then** the UI remains accessible and shows current status and download queue (NFR-18, AC-19).

**Given** a database refresh operation is in progress,
**When** I make health check or status API requests,
**Then** they complete successfully within performance targets (NFR-19, AC-20).

**Given** a database refresh operation is in progress,
**When** I perform queue management operations (view, add, remove items),
**Then** they execute normally without being blocked by the refresh operation (NFR-19, AC-21).

**Given** concurrent database refresh and user operations,
**When** both are executing,
**Then** the system maintains data consistency and operational integrity.

---

### Story 1.7: Add thread synchronization to active_downloads dictionary access

As a system administrator,
I want the MTV Downloader web interface to have proper thread synchronization for the active_downloads dictionary so that concurrent access from multiple threads does not cause race conditions or data corruption.

**Acceptance Criteria:**

**Given** multiple background download tasks are running simultaneously,
**And** each task tries to update the status of a download,
**When** the tasks execute concurrently,
**Then** the application should not crash or corrupt data,
**And** all download statuses should be properly recorded.

**Given** the web interface has active downloads,
**And** multiple users are viewing download status simultaneously,
**And** background download tasks are updating statuses,
**When** requests are processed concurrently,
**Then** all status queries should return consistent data,
**And** no race conditions should occur.

**Given** there are active downloads running,
**When** the application is shut down gracefully,
**Then** all active downloads should be safely managed,
**And** no data corruption should occur during shutdown.

---

### Story 1.8: Implement proper locking for all shared mutable state

As a system administrator,
I want the MTV Downloader web interface to have proper locking mechanisms for all shared mutable state so that the application remains stable and data integrity is maintained under concurrent usage.

**Acceptance Criteria:**

**Given** the application has multiple shared mutable state variables,
**When** multiple threads access these variables simultaneously,
**Then** all shared state should be protected from race conditions,
**And** data integrity should be maintained.

**Given** database refresh is happening in background,
**And** download operations are running simultaneously,
**When** both operations access shared resources,
**Then** no conflicts should occur,
**And** both operations should complete successfully.

**Given** global variables that store application state,
**When** multiple threads modify these variables,
**Then** all modifications should be atomic and consistent,
**And** no partial updates should occur.

---

### Story 1.9: Implement comprehensive concurrency improvements for shared state

As a system administrator,
I want the MTV Downloader web interface to have comprehensive thread safety measures so that the application remains stable, reliable, and performs well under concurrent usage with multiple simultaneous downloads and requests.

**Acceptance Criteria:**

**Given** the application handles multiple concurrent download operations,
**When** various threads access shared state simultaneously,
**Then** all operations should complete successfully without race conditions,
**And** data integrity should be maintained throughout.

**Given** a database refresh is in progress,
**And** download operations are running simultaneously,
**When** both operations access shared resources,
**Then** neither operation should interfere with the other,
**And** both should complete successfully.

**Given** multiple threads are operating concurrently,
**When** unexpected errors occur during shared state access,
**Then** the application should handle errors gracefully,
**And** should not crash or leave shared state in inconsistent state.

---

### Story 1.10: Improve Database Refresh Cadence, Status, and Logging

As a self-hosting user,
I want database refreshes to run on an explicit cadence with clear UI status and logs,
So that searches use fresh data without blocking normal app usage or hiding refresh failures.

**Acceptance Criteria:**

**Given** default configuration,
**When** the service starts,
**Then** database refresh is scheduled every 24 hours unless the user configures a different interval (FR-34).

**Given** a user performs a search or starts a download,
**When** no manual or scheduled refresh is active,
**Then** the operation does not implicitly trigger a database refresh (FR-35).

**Given** a database refresh has completed successfully,
**When** the user views status in the UI or calls the status API,
**Then** the last successful update time and database age are shown when available (FR-36).

**Given** a database refresh starts, succeeds, or fails,
**When** logs are inspected,
**Then** refresh trigger source, outcome, and duration are recorded (FR-37).

---

### Story 1.11: Consolidate mtv_dl Dependency Integration

As a maintainer,
I want the app to use one canonical `mtv_dl` dependency source,
So that local, test, and container behavior do not depend on conflicting import paths.

**Acceptance Criteria:**

**Given** the project dependency configuration,
**When** dependencies are installed,
**Then** `mtv_dl` is provided by the selected canonical source, preferably the packaged dependency (FR-38).

**Given** the repository is inspected,
**When** duplicate vendored or submodule `mtv_dl` copies are found,
**Then** they are removed or made inactive so they cannot conflict with the canonical dependency (FR-38).

**Given** local tests and container startup run,
**When** `mtv_dl` is imported,
**Then** both environments import the same canonical source.

---

### Story 1.12: Publish Container Images from Main Branch

As a self-hosting user,
I want a project-published container image built from main,
So that installation does not require building the image locally.

**Acceptance Criteria:**

**Given** changes land on the main branch,
**When** the GitHub workflow runs successfully,
**Then** it builds and publishes a container image for the project (FR-39).

**Given** the image is published,
**When** I read the documentation,
**Then** I can find the image location and run it with documented configuration, data, and download mounts (FR-30, FR-39).

**Given** the documented image is run with the required mounts,
**When** I call the readiness endpoint,
**Then** it reports ready and persists mounted data across restart (FR-30, FR-31).

---

### Story 1.13: Implement Download Naming Patterns

As a user,
I want downloads to use the same naming and folder behavior as `mtv_dl`,
So that files land in the expected shared folder with recognizable names.

**Acceptance Criteria:**

**Given** a queued item starts downloading,
**When** the backend delegates to `mtv_dl.Downloader`,
**Then** it uses `mtv_dl` naming and folder structure behavior rather than writing `download.mp4` in the project root (FR-13).

**Given** a completed download,
**When** the system verifies the files,
**Then** all file names match the configured naming behavior and files are located under the configured target directory (FR-14).

### Epic 2: Search Functionality

**Goal**: Users can search the `mtv_dl` database using filters.

### Story 2.1: Implement Search API Endpoint

As a user,
I want to search videos using `mtv_dl`-compatible filters,
So that I can find shows to download.

**Acceptance Criteria:**

**Given** a populated `mtv_dl` database,
**When** I call `GET /search?q=title=Example`,
**Then** it returns matching videos with metadata (FR-1, FR-4).

**Given** invalid filters,
**When** I submit them,
**Then** the API rejects them with a validation error (NFR-7).

---

### Story 2.2: Validate Filter Operators/Fields

As a user,
I want to use filter operators (`=`, `!=`, `+`, `-`) and fields (`title`, `channel`, etc.),
So that I can refine my searches.

**Acceptance Criteria:**

**Given** valid operators/fields,
**When** I submit a search,
**Then** the API processes them correctly (FR-2, FR-3).

**Given** unsupported operators/fields,
**When** I submit them,
**Then** the API returns a `400 Bad Request` (NFR-1).

---

### Story 2.3: Build Search UI

As a user,
I want a search form and results list in the UI,
So that I can search without using the API directly.

**Acceptance Criteria:**

**Given** the search page,
**When** I enter filters and submit,
**Then** results display metadata (title, channel, size, etc.) (FR-5).

**Given** no results,
**When** I search,
**Then** the UI shows a "No results" message.

### Epic 3: Download Queue Management

**Goal**: Users can queue, monitor, and manage downloads.

### Story 3.2: Implement Queue API Endpoints

As a user,
I want to add/remove downloads via API,
So that I can manage my download queue.

**Acceptance Criteria:**

**Given** a video ID,
**When** I call `POST /queue` with `{ "video_id": "123" }`,
**Then** it adds the video to the queue (FR-15).

**Given** a pending queue item,
**When** I call `DELETE /queue/{id}`,
**Then** it removes the item (FR-18).

---

### Story 3.3: Enforce Single Active Download

As a user,
I want only one download to run at a time,
So that my system resources aren’t overwhelmed.

**Acceptance Criteria:**

**Given** an active download,
**When** I add another item to the queue,
**Then** it remains `pending` until the active download completes (FR-16).

---

### Story 3.4: Build Queue UI

As a user,
I want to view and manage the queue in the UI,
So that I can monitor download status.

**Acceptance Criteria:**

**Given** the queue page,
**When** I view it,
**Then** it shows `pending`, `downloading`, `completed`, and `failed` items (FR-17).

**Given** a pending item,
**When** I click "Remove",
**Then** it disappears from the queue (FR-18).

---

### Story 3.5: Integrate `mtv_dl.Downloader`

As a user,
I want downloads to use existing `mtv_dl` behavior,
So that my files are saved correctly.

**Acceptance Criteria:**

**Given** a queued item,
**When** it starts downloading,
**Then** it uses `mtv_dl.Downloader` with configured options (FR-7, FR-8, FR-9).

### Epic 4: Scheduler for Auto-Downloads

**Goal**: Users can schedule recurring searches and auto-enqueue matches.

### Story 4.1: Implement Scheduler Backend

As a user,
I want to create/edit scheduled queries with cron-like syntax,
So that I can auto-download new matches.

**Acceptance Criteria:**

**Given** a valid cron expression,
**When** I schedule a query,
**Then** it runs at the specified time (FR-24).

**Given** an invalid cron expression,
**When** I submit it,
**Then** the scheduler rejects it (NFR-7).

---

### Story 4.2: Auto-Enqueue Non-Duplicates

As a user,
I want the scheduler to auto-enqueue new matches,
So that I don’t download duplicates.

**Acceptance Criteria:**

**Given** a scheduled query match,
**When** its hash/URL isn’t in the queue,
**Then** it’s added to `pending` (FR-25).

**Given** a duplicate match,
**When** the scheduler runs,
**Then** it’s ignored (FR-25).

---

### Story 4.3: Build Scheduler UI

As a user,
I want to view and manage scheduled queries in the UI,
So that I can monitor auto-downloads.

**Acceptance Criteria:**

**Given** the scheduler page,
**When** I view it,
**Then** it shows job status, last run result, and auto-enqueued count (FR-26).

### Epic 5: Responsive UI & UX

**Goal**: Users can interact with the app across devices.

### Story 5.1: Build Responsive Search/Queue UI

As a user,
I want the UI to adapt to my device,
So that I can use it on mobile or desktop.

**Acceptance Criteria:**

**Given** a 360px/768px/1280px viewport,
**When** I open the UI,
**Then** controls remain usable without horizontal scrolling (NFR-13).

**Given** a long-running action,
**When** it starts,
**Then** a loading state appears within 1 second (NFR-14).

---

### Story 5.2: Style Frontend with CSS

As a user,
I want a clean, functional UI,
So that I can navigate easily.

**Acceptance Criteria:**

**Given** the UI,
**When** I view it,
**Then** it uses plain CSS (no Tailwind) for styling.

**Given** the UI,
**When** I interact with it,
**Then** controls have visible focus states (accessibility).
