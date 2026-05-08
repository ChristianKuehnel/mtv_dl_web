---
project_name: 'mtv_dl_web'
user_name: 'Christian'
date: '2026-05-07'
stepsCompleted: ['step-1-init', 'step-2-context', 'step-3-starter', 'step-4-decisions', 'step-5-patterns', 'step-6-structure', 'step-7-validation']
inputDocuments: ['_bmad-output/planning-artifacts/prd.md', 'spec/sw_architecture.md']
lastStep: 'step-3-starter'
---

## Starter Template Evaluation

### Primary Technology Domain

Single-user self-hosted web application with a Python FastAPI backend and static HTML/CSS/JavaScript frontend.

### Starter Options Considered

| Option | Decision | Reason |
| --- | --- | --- |
| Existing repository structure with custom minimal FastAPI app | Selected | Best matches integration-first scope and avoids unnecessary SaaS/database/auth assumptions. |
| `uv init` Python project | Not selected for project creation | Useful for fresh Python projects, but this repository already exists. `uv` remains the dependency and build foundation. |
| FastAPI Full Stack Template | Rejected | Provides React, PostgreSQL, auth, Traefik, generated clients, and multi-service patterns that conflict with MVP constraints. |
| Tailwind Play CDN | Rejected | Adds an external runtime dependency and Tailwind documents it as development-oriented; plain local CSS better matches the self-hosted MVP. |

### Selected Starter: Existing Repository + Minimal Custom App

**Rationale for Selection:**

The application is a lightweight browser interface over existing `mtv_dl` behavior. A custom minimal app preserves the PRD constraints: no external services, no auth, no additional application database, static frontend, mounted configuration/data/download paths, and direct reuse of `mtv_dl.Database` and `mtv_dl.Downloader`.

**Initialization Command:**

No new project starter command is required because the repository already exists.

For dependency and build management, use the existing `uv` project workflow:

```bash
uv sync
```

**Architectural Decisions Provided by This Foundation:**

**Language & Runtime:**
Python `>=3.10` with FastAPI and Pydantic models for API validation.

**Frontend:**
Static HTML/CSS/JavaScript served by the backend from `src/frontend/`.

**Styling:**
Plain local CSS stored with frontend assets. No Tailwind CDN and no frontend build pipeline are required for MVP.

**Build Tooling:**
`uv` manages dependencies and lockfile-based reproducible installs.

**Testing Framework:**
`pytest`, `fastapi.testclient`, `pytest-asyncio`, and container smoke tests.

**Code Organization:**
Backend entrypoint in `src/main.py`, static frontend in `src/frontend/`, integrated `mtv_dl` source under `src/mtv_dl/`, tests under `tests/`.

**Development Experience:**
Run app and tests through `uv`; verify quality with configured linting, type checks, frontend formatting, Dockerfile linting, ShellCheck, and container smoke tests.

**Note:**
Project initialization is already complete. The first implementation architecture story should verify and normalize the repository structure against this selected foundation. Older Tailwind CDN references in legacy specs are superseded by this architecture decision.

## Core Architectural Decisions

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:**
4 areas where AI agents could make different implementation choices.

### Naming Patterns

**API Naming Conventions:**
- Endpoints: Minimalist REST (e.g., `/search`, `/queue`).
- File naming: `searchService.js` (camelCase for JS), `search_service.py` (snake_case for Python).
- Variables: `videoId` (JS), `video_id` (Python).

### Structure Patterns

**Project Organization:**
- Tests: `tests/` directory (separate from source).
- Frontend assets: `src/frontend/css/`, `src/frontend/js/`.

### Format Patterns

**API Response Formats:**
- Direct responses (e.g., `{ videos: [...] }`).
- Structured errors (e.g., `{ error: { code, message } }`).

### Process Patterns

**Error Handling Patterns:**
- Global middleware for HTTP errors (FastAPI).
- Per-component loading indicators (JS).

### Enforcement Guidelines

**All AI Agents MUST:**
- Follow naming conventions (camelCase for JS, snake_case for Python).
- Place tests in `tests/`.
- Use direct API responses and structured errors.

## Project Structure & Boundaries

### Complete Project Directory Structure

```
mtv_dl_web/
├── README.md
├── pyproject.toml          # uv project config
├── uv.lock                 # uv lockfile
├── .env                    # Environment variables
├── .env.example            # Example env file
├── .gitignore
├── Dockerfile              # Alpine Linux container
├── docker-compose.yml      # Optional: Local dev setup
├── src/
│   ├── main.py             # FastAPI entrypoint
│   ├── config.py           # App configuration
│   ├── frontend/           # Static frontend
│   │   ├── index.html
│   │   ├── css/
│   │   │   └── styles.css
│   │   ├── js/
│   │   │   ├── search.js   # Search UI logic
│   │   │   ├── queue.js    # Queue management
│   │   │   └── downloads.js # Downloads view
│   │   └── assets/         # Static assets (images, etc.)
│   └── mtv_dl/            # Integrated mtv_dl modules
│       ├── __init__.py
│       ├── database.py    # Reused mtv_dl.Database
│       └── downloader.py  # Reused mtv_dl.Downloader
├── tests/
│   ├── test_api.py        # API endpoint tests
│   ├── test_integration.py # Integration tests
│   └── conftest.py        # Test fixtures
└── _bmad-output/          # BMad artifacts (ignored in git)
```

### Architectural Boundaries

**API Boundaries:**
- Endpoints:
  - `GET /search`: Search videos (query params: `q`, `limit`).
  - `GET /queue`: List queued downloads.
  - `POST /queue`: Add to queue (body: `{ video_id }`).
  - `DELETE /queue/{id}`: Remove from queue.
  - `GET /downloads`: List completed downloads.

**Component Boundaries:**
- Frontend: Vanilla JS modules (`search.js`, `queue.js`, `downloads.js`).
- Backend: FastAPI routes in `main.py` with Pydantic validation.

**Data Boundaries:**
- Database: Reuse `mtv_dl.Database` (no modifications).
- File System: Mounted volumes for downloads/config (Docker).

### Requirements Mapping

| Feature               | Location                     | Files                          |
|-----------------------|------------------------------|--------------------------------|
| Search UI             | `src/frontend/`              | `search.js`, `index.html`      |
| Queue Management      | `src/frontend/` + API        | `queue.js`, `main.py`          |
| Downloads View        | `src/frontend/`              | `downloads.js`                 |
| API Endpoints         | `src/main.py`                | FastAPI routes                 |
| `mtv_dl` Integration  | `src/mtv_dl/`                | `database.py`, `downloader.py` |

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**
- All decisions (FastAPI, vanilla JS, `mtv_dl` integration) work together without conflicts.
- Technology versions (Python 3.10+, FastAPI) are compatible.

**Pattern Consistency:**
- Naming conventions (camelCase for JS, snake_case for Python) align with the tech stack.
- Error handling (structured HTTP errors) is consistent across API boundaries.

**Structure Alignment:**
- Project structure supports all architectural decisions (e.g., `src/mtv_dl/` for integration).
- Boundaries (API, frontend, data) are clearly defined and respected.

### Requirements Coverage Validation ✅

**Functional Requirements Coverage:**
- All PRD requirements (search, queue, downloads) are supported by the architecture.
- API endpoints (`/search`, `/queue`, `/downloads`) map directly to PRD features.

**Non-Functional Requirements Coverage:**
- Single-user, self-hosted constraints are met (no auth, no external DB).
- Containerization (Docker) supports self-hosted deployment.

### Implementation Readiness Validation ✅

**Decision Completeness:**
- All critical decisions documented (e.g., caching, API design, error handling).
- Technology versions verified (Python 3.10+, FastAPI).

**Structure Completeness:**
- Directory tree is fully defined (e.g., `src/frontend/js/` for UI logic).
- Integration points (API, `mtv_dl`) are clearly specified.

**Pattern Completeness:**
- Consistency rules (naming, error handling) are enforceable.
- Examples provided for all major patterns (e.g., API responses, error formats).

### Architecture Readiness Assessment

**Overall Status:** **READY FOR IMPLEMENTATION**

**Confidence Level:** High

**Key Strengths:**
- Minimalist, self-hosted design with zero external dependencies.
- Direct `mtv_dl` integration with clear boundaries.
- Consistent patterns (naming, error handling, structure).

**Implementation Handoff:**
- **First Step**: Implement FastAPI endpoints in `src/main.py` (see API Boundaries).
- **AI Agent Guidelines**: Follow all architectural decisions, patterns, and structure exactly as documented.

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- **Caching Strategy**: No caching for search/queue operations. Direct calls to `mtv_dl` for simplicity and data freshness.
- **API Design**: Minimalist REST endpoints (`/search`, `/queue`, `/downloads`).

**Important Decisions (Shape Architecture):**
- **Frontend State Management**: Vanilla JS for simplicity.
- **Containerization**: Docker for Alpine Linux with mounted volumes for persistence.
- **Error Handling**: Standardized HTTP error responses (4xx/5xx).

### Data Architecture

- **Database**: Reuse `mtv_dl.Database` without modification.
- **Caching**: No caching layer. All operations directly interact with `mtv_dl` for simplicity and consistency.
- **Validation**: Pydantic models for API requests/responses.

### API & Communication Patterns

- **API Design**: Minimalist REST endpoints:
  - `GET /search`: Search videos with query parameters.
  - `GET /queue`: List queued downloads.
  - `POST /queue`: Add to download queue.
  - `DELETE /queue/{id}`: Remove from queue.
  - `GET /downloads`: List completed downloads.
- **Error Handling**: Structured HTTP error responses (e.g., `{ "error": { "code": 404, "message": "Video not found", "details": "..." } }`).
- **Rate Limiting**: None (single-user application).

### Frontend Architecture

- **State Management**: Vanilla JavaScript (no libraries) for zero dependencies. Use `document.querySelector` and manual DOM updates.
- **Component Structure**: Modular JS/CSS for search, queue, and download views.
- **Routing**: Server-side routing for simplicity.

### Infrastructure & Deployment

- **Containerization**: Docker for Alpine Linux with mounted volumes for configuration, data, and downloads.
- **CI/CD**: Basic GitHub Actions for linting and testing.
- **Configuration**: Environment variables for paths (e.g., `TARGET_DIR`).
