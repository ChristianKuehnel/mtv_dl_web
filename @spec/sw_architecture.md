# MTV Downloader Web Interface - Software Architecture

## Overview
This document describes the software architecture for a lightweight web interface for the MTV Downloader project. The system provides a RESTful API between the web frontend and Python backend, supporting concurrent web requests and downloads for a single user.

## System Components

### 1. Backend Architecture
- Implement a web-API wrapper around the existing functionality of mtv_dl
- **Framework**: FastAPI (Python 3.10+)
- **Concurrency Model**: Async/Await with ThreadPoolExecutor for blocking operations
- **Database**: SQLite (only for existing mtv_dl database integration)
- **Configuration**: Use yaml-config files for service configuration, do not create another database.
- **API Design**: RESTful JSON API
- **Integration Approach**: Reuse existing mtv_dl modules without duplicating database logic

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
  - Database initialization and connection management
  - Concurrent download handling with background tasks
  - REST API endpoints for frontend communication
  - Queries and downloads are handled by the mtv_dl functionality
  - Queue management for download scheduling
  - Series detection and handling capabilities

- **Database Integration**: `mtv_dl/src/mtv_dl/mtv_dl.py`
  - Existing mtv_dl Database class for querying shows
  - Downloader class for downloading content
  - Re-use existing business logic, do *not* talk directly to the database
  - Use the same filter arguments as mtv_dl
  - Leverage existing filtering and download logic

#### Frontend (Static Assets)
- **HTML**: `src/frontend/index.html`
  - Main user interface with search, results, and download controls
  - Responsive design with Tailwind CSS

## Integration with Existing MTV DL Code

### Module Integration Approach
- The backend imports mtv_dl modules directly from their source location
- All database operations go through the existing mtv_dl Database class
- Download operations utilize the existing mtv_dl Downloader class
- All existing filter logic and parsing capabilities are reused
- Configuration passes through mtv_dl's native configuration system

### Packaging Strategy
- **Container Build**: Include mtv_dl source code as submodule or copy it into the container
- **Dependency Management**: Use uv or pip to incdule the mtv_dl dependencies
- **Python Path**: Ensure mtv_dl modules are in Python path for imports
- **Docker Layering**: Place mtv_dl code in appropriate layers to enable caching
- **Version Pinning**: Pin mtv_dl version to ensure stability

### Source Integration Details
- mtv_dl modules are imported as Python packages in the backend
- Database connection strings and paths are preserved from mtv_dl
- All CLI argument parsing is maintained through mtv_dl's native system
- Existing logging and error handling patterns are preserved
- Configuration files are passed through to mtv_dl's configuration system

## API Design

### REST Endpoints

1. **GET /** - Serve main HTML page
2. **GET /health** - Health check endpoint
3. **POST /api/search** - Search for shows with filters
4. **POST /api/download** - Initiate downloads with parameters
5. **GET /api/download/status/{download_id}** - Get specific download status
6. **GET /api/download/status** - Get all active download statuses
7. **POST /api/database/update** - Trigger manual database update
8. **GET /api/scheduler/queries** - Get configured scheduled queries
9. **POST /api/scheduler/queries** - Add new scheduled query
10. **DELETE /api/scheduler/queries/{query_id}** - Remove scheduled query

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

#### ScheduledQuery
```json
{
  "id": "string",
  "filters": ["channel=ARD", "topic='extra 3'"],
  "cron_expression": "0 2 * * *",
  "enabled": true,
  "last_run": "datetime",
  "next_run": "datetime"
}
```

## Concurrency & Performance

### Request Handling
- **Web Requests**: Async processing using FastAPI
- **Download Operations**: Thread pool executor for blocking I/O operations
- **Background Processing**: Background tasks using FastAPI's BackgroundTasks
- **Database Access**: Single-threaded access to SQLite with proper locking
- **Queue Management**: Support for multiple queued downloads with scheduling

### Threading Model
1. Web requests are handled asynchronously
2. Download operations are processed with queue management
3. Status updates are managed with in-memory dictionary
4. Scheduler runs periodically to monitor and update database
4. Scheduler runs periodically to monitor and update database

## Deployment Architecture

### Containerization
- **Base Image**: Alpine Linux (lightweight, secure)
- **Port Exposure**: Port 8000 (HTTP) - configurable via environment
- **Persistent Storage**: Volume mounts for database and config
- **Container Runtime**: Docker and Podman compatible

### Configuration
- **Configuration File**: `/config/mtv_dl_web.yaml` (optional)
- **Environment Variables**: 
  - `PORT`: Service port (default: 8000)
  - `DATABASE_PATH`: Database file location (default: `/data/.mtv_dl_web`)
  - `TARGET_DIR`: Default download target (default: `/downloads`)
  - `SERIES_TARGET_DIR`: Target directory for series downloads (default: `/downloads/series`)
  - `LOG_LEVEL`: Logging level (default: INFO)
  - `SCHEDULER_CRON`: Cron expression for periodic database updates (default: "0 2 * * *")

### Volume Mounts
1. **/data**: Persistent storage for MTV database files
2. **/config**: Configuration files (optional)
3. **/downloads**: Download destination directory
4. **/downloads/series**: Series download destination directory (for series-mode downloads)

### Docker Deployment Example
```bash
docker run -d \
  --name mtv-downloader \
  -p 8000:8000 \
  -v /path/to/data:/data \
  -v /path/to/downloads:/downloads \
  -v /path/to/config:/config \
  fnep/mtv_dl_web:latest
```

### Podman Deployment Example
```bash
podman run -d \
  --name mtv-downloader \
  -p 8000:8000 \
  -v /path/to/data:/data \
  -v /path/to/downloads:/downloads \
  -v /path/to/config:/config \
  fnep/mtv_dl_web:latest
```

### Configuration File Structure
```yaml
# /config/mtv_dl_web.yaml
port: 8000
database_path: /data/.mtv_dl_web
target_dir: /downloads
series_target_dir: /downloads/series
log_level: INFO
scheduler_cron: "0 2 * * *"
```

### Environment Variable Precedence
1. Environment variables (highest priority)
2. Configuration file
3. Default values (lowest priority)

### Health Checks
- **Endpoint**: `/health`
- **Method**: GET
- **Expected Response**: 200 OK
- **Purpose**: Container orchestration readiness check

## Future Scalability

While optimized for single user, the architecture supports:
- Easy addition of user accounts
- Multi-threading enhancements for download processing
- Database abstraction layer for future storage options
- Plugin architecture for additional download sources
- Enhanced scheduler capabilities for more complex scheduling