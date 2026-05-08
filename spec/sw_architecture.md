# MTV Downloader Web Interface - Software Architecture

## Overview
This document describes the software architecture for a lightweight web interface for the MTV Downloader project. The system provides a RESTful API between the web frontend and Python backend, supporting concurrent web requests and downloads for a single user.

## System Components

### 1. Backend Architecture
- Implement only a minmal web-API wrapper around the existing functionality of mtv_dl
- **Framework**: FastAPI (Python 3.10+)
- **Concurrency Model**: Async/Await with ThreadPoolExecutor for blocking operations
- **Database**: SQLite (only for existing mtv_dl database integration)
- **Configuration**: Use yaml-config files for service configuration, do not create another database.
- **Scheduling**: APScheduler with `AsyncIOScheduler` for background query searches and cron-like schedules.
- **API Design**: RESTful JSON API

### 2. Frontend Architecture
- **Framework**: Pure HTML/CSS/JavaScript (no frameworks)
- **Styling**: Tailwind CSS CDN
- **UI Components**:
  - Search interface with filters
  - Results display with selection
  - Download options
  - Real-time download status monitoring

### 3. Core Modules

#### Backend (Python)
- **Main Application**: `src/main.py`
  - FastAPI application with routes for search, download, and status
  - download handling with background tasks, only one download at a time
  - scheduled query searches run via APScheduler `AsyncIOScheduler`, started and stopped in the FastAPI lifespan handler
  - REST API endpoints for frontend communication
  - queries and downloads are handled by the mtv_dl functionality

- **Database Integration**: `mtv_dl/src/mtv_dl/mtv_dl.py`
  - Existing mtv_dl Database class for querying shows
  - Downloader class for downloading content
  - re-use existing business logic, do *not* talk directly to the database
  - use the same filter arguments as mtv_dl

#### Frontend (Static Assets)
- **HTML**: `src/frontend/index.html`
  - Main user interface with search, results, and download controls
  - Responsive design with Tailwind CSS

## API Design

### REST Endpoints

1. **GET /** - Serve main HTML page
2. **GET /health** - Health check endpoint
3. **POST /api/search** - Search for shows with filters
4. **POST /api/download** - Initiate downloads with parameters
5. **GET /api/download/status/{download_id}** - Get specific download status
6. **GET /api/download/status** - Get all active download statuses

### Data Models

#### SearchFilters
```json
{
  "filters": ["channel=ARD", "topic='extra 3'"]
}
```

#### ShowItem (from database)
```json
{
  "hash": "string",
  "channel": "string",
  "title": "string",
  "topic": "string",
  "size": 0,
  "start": "datetime",
  "duration": "string",
  "age": "string",
  "region": "string",
  "downloaded": "datetime"
}
```

#### DownloadRequest
```json
{
  "filters": ["channel=ARD", "topic='extra 3'"],
  "quality": "url_http",
  "target_directory": "./downloads",
  "include_subtitles": true,
  "include_nfo": true,
  "merge_to_mkv": false
}
```

#### DownloadStatus
```json
{
  "id": "string",
  "status": "queued|downloading|completed|failed",
  "progress": 0.0,
  "message": "string",
  "file_path": "string"
}
```

## Concurrency & Performance

### Request Handling
- **Web Requests**: Async processing using FastAPI
- **Download Operations**: Thread pool executor for blocking I/O operations
- **Background Processing**: Background tasks using FastAPI's BackgroundTasks
- **Database Access**: Single-threaded access to SQLite with proper locking

### Threading Model
1. Web requests are handled asynchronously
2. Download operations are processed single-threaded, matching the existing mtv_dl logic
3. Scheduled query searches are triggered by APScheduler and execute blocking mtv_dl work through the same ThreadPoolExecutor path used by manual searches/downloads
4. Status updates are managed with in-memory dictionary

### Scheduled Query Search
- **Framework**: Use `APScheduler` (`apscheduler.schedulers.asyncio.AsyncIOScheduler`) as the only scheduling framework.
- **Triggers**: Use APScheduler `CronTrigger` for cron-like expressions configured in YAML.
- **Lifecycle**: Start the scheduler during FastAPI application startup and shut it down during application shutdown via the lifespan handler.
- **Persistence**: Store scheduled query definitions in the YAML configuration file. Do not use APScheduler job stores or create a separate scheduler database.
- **Execution**: Scheduler jobs call the existing mtv_dl search/download integration; do not duplicate query logic or access SQLite directly.
- **Concurrency**: Configure scheduler jobs with `max_instances=1` and avoid overlapping executions of the same scheduled query.
- **Container Behavior**: The scheduler runs in-process with the FastAPI application; no external cron daemon or sidecar service is required.

## Deployment Architecture

### Single-User Focus
- Optimized for single-user experience
- No user authentication required
- Simple configuration with default paths

### Lightweight Design
- Minimal dependencies (FastAPI, APScheduler, SQLite, standard library)
- No external services required
- Container-ready with Docker support

## Security Considerations

- Input validation on all API endpoints
- No sensitive data stored in state
- Limited exposure of internal paths
- Sanitized user inputs for database queries

## Future Scalability

While optimized for single user, the architecture supports:
- Easy addition of user accounts
- Multi-threading enhancements
- Database abstraction layer for future storage options
- Plugin architecture for additional download sources

## Development & Testing

### Tools Used
- FastAPI for API framework
- APScheduler for scheduled background query searches
- config files for local persistence
- Pydantic for data validation
- HTML/CSS/JS for frontend

### Testing Strategy
- Unit tests for individual components
- Integration tests for API endpoints
- Manual UI testing for frontend interaction

### Testing Framework
This project will use the following testing frameworks and approaches:

1. **Unit Testing**
   - Framework: `pytest` (Python)
   - Purpose: Test individual functions and classes in isolation
   - Coverage: Core business logic, data models, utility functions

2. **Integration Testing**
   - Framework: `pytest` with `httpx` or `fastapi.testclient`
   - Purpose: Test API endpoints and interactions between components
   - Coverage: REST API endpoints, request/response handling, database operations

3. **Frontend Testing**
   - Framework: `Jest` (JavaScript)
   - Purpose: Test JavaScript functionality and UI interactions
   - Coverage: Form validation, event handlers, DOM manipulation

4. **End-to-End Testing**
   - Framework: `Playwright` or `Cypress` 
   - Purpose: Test complete user flows and browser interactions
   - Coverage: Full user journey from search to download

5. **Static Analysis**
   - Framework: `mypy` (Python type checking)
   - Framework: `flake8` (Python linting)
   - Framework: `prettier` (JavaScript/HTML/CSS formatting)
   - Purpose: Catch errors early and maintain code quality

6. **Smoke Testing**
   - Framework: Custom Python scripts
   - Purpose: Verify core functionality works end-to-end
   - Coverage: Server startup, health check endpoint, basic UI rendering

7. **Docker Testing**
   - Framework: `Podman`/`Docker` with automated tests
   - Purpose: Validate container deployment and runtime behavior
   - Coverage: Image building, container startup, health checks

Each test suite will be integrated into CI/CD pipeline and run during development and release processes to ensure quality and prevent regressions.
