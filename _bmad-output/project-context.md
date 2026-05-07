---
project_name: 'mtv_dl_web'
user_name: 'Christian'
date: '2026-05-07'
sections_completed: ['technology_stack', 'definition_of_done', 'language_specific_rules', 'framework_specific_rules', 'testing_rules', 'code_quality_rules', 'development_workflow_rules', 'critical_dont_miss_rules']
existing_patterns_found: 8
status: complete
rule_count: 38
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

- **Runtime:** Python >=3.10
- **Web Framework:** FastAPI >=0.115.0
- **ASGI Server:** uvicorn[standard] >=0.31.1
- **Validation:** Pydantic >=2.9.2
- **Dependency Management:** uv (astral.sh)
- **Build System:** uv-build
- **Frontend:** Pure HTML/CSS/JS, Tailwind CSS CDN
- **Database:** SQLite (via mtv_dl's Database class)
- **Container:** Docker (python:3.11-slim), Podman

**Dev Dependencies:**
- pytest >=8.4, <9.1
- mypy >=1.16.0 (strict mode)
- black >=24.4.2
- httpx >=0.28.1
- pytest-cov >=4.1.0
- pytest-asyncio >=0.23.0
- pre-commit >=3.5.0
- types-requests >=2.32.0.20240914

## Definition of Done

Before each task is considered complete, the following criteria must be met:
- Functionality covered by unit tests, all tests must be passing
- Use black for Python code formatting
- Add HTML and JS code formatting using Prettier
- Use Python type checking with mypy for validation
- Use hadolint as formatter and linter for Docker files
- Use ShellCheck as linter for shell scripts
- `scripts/linting.sh` must pass and changes were committed to git
- Add smoke test to check if the backend starts and health check returns 200 OK
- Add smoke test to deploy the container using Podman and verify health check

## Critical Implementation Rules

### Language-Specific Rules (Python)

- **mtv_dl import**: Always use `sys.path.insert(0, str(Path(__file__).parent / "mtv_dl" / "src"))` then `from mtv_dl.mtv_dl import Database, Downloader`
- **Type annotations**: All functions must have type hints (mypy strict mode enforced)
- **Error handling**: Use `HTTPException` with specific status codes; log failures with `logger.error()` before raising
- **Async pattern**: FastAPI route handlers are `async def`; blocking I/O uses `ThreadPoolExecutor` or `BackgroundTasks`
- **Pydantic models**: Define request/response models with `BaseModel` for all API endpoints
- **Imports order**: stdlib → third-party → local, separated by blank lines

### Framework-Specific Rules (FastAPI)

- **Route patterns**: Use `@app.get()`, `@app.post()` decorators; all handlers are `async def`
- **Static files**: Mount frontend directory with `app.mount("/static", StaticFiles(directory=...), name="static")`
- **CORS**: Enable with `CORSMiddleware(allow_origins=["*"], ...)` for development
- **Background tasks**: Use FastAPI's `BackgroundTasks` parameter for download processing
- **Health endpoint**: Always expose `GET /health` returning `{"status": "healthy"}`
- **Error responses**: Raise `HTTPException(status_code=404, ...)` for not found, `500` for server errors
- **Root route**: Serve `index.html` with `response_class=HTMLResponse`, fallback to inline HTML

### Testing Rules

- **Framework**: pytest with `--doctest-modules` flag set in pyproject.toml
- **API testing**: Use `TestClient` from `fastapi.testclient`
- **Async tests**: Use `pytest-asyncio` for async endpoint tests
- **Fixtures**: Use pytest fixtures for app/client setup
- **Coverage**: Use `pytest-cov` for coverage reporting
- **Mocking**: Use `unittest.mock` for mtv_dl dependencies
- **Test location**: All tests in `tests/` directory

### Code Quality & Style Rules

- **Python formatting**: black with line-length 120 (convention from original setup)
- **Type checking**: mypy strict mode — `strict = true`, `warn_unused_ignores = true`, `ignore_missing_imports = true`
- **Frontend formatting**: Prettier for HTML/JS/CSS
- **Docker linting**: hadolint for Dockerfile validation
- **Shell scripts**: ShellCheck for shell script linting
- **Pre-commit**: All linting checks must pass via `scripts/linting.sh` before commit

### Development Workflow Rules

- **Phase order**: Follow 4-phase plan: Basic UI → mtv_dl Integration → Features → Container
- **Single download**: Only one active download at a time; queue others
- **Container first**: All features must work in Docker/Podman before considered done
- **No auth**: Single-user focus, no authentication required
- **Config**: Use yaml config files at `/config/mtv_dl_web.yaml`, not additional databases
- **Database reuse**: Use mtv_dl's existing Database/Downloader classes — do NOT talk to SQLite directly

### Critical Don't-Miss Rules

- **Never reimplement mtv_dl logic**: Always delegate to mtv_dl's `Database.filtered()` and `Downloader.download()` — no direct SQLite queries
- **sys.path hack**: The mtv_dl import requires `sys.path.insert(0, ...)` BEFORE the import statement
- **Downloader args**: `Downloader.download()` takes `quality` as a tuple of URL types, not a single string
- **Database file**: Lives at `~/.mtv_dl_web/filmliste.sqlite` — ensure directory exists before init
- **Frontend path**: Static files are served from `src/frontend/` mounted at `/static`
- **No ruff config**: Currently no ruff in pyproject.toml; don't assume it's available

---

## Usage Guidelines

**For AI Agents:**

- Read this file before implementing any code
- Follow ALL rules exactly as documented
- When in doubt, prefer the more restrictive option
- Update this file if new patterns emerge

**For Humans:**

- Keep this file lean and focused on agent needs
- Update when technology stack changes
- Review quarterly for outdated rules
- Remove rules that become obvious over time

Last Updated: 2026-05-07
