# MTV Downloader Web Interface - Software Architecture

## Overview
This document describes the software architecture for a lightweight web interface for the MTV Downloader project. The system provides a RESTful API between the web frontend and Python backend, supporting concurrent web requests and downloads for a single user.

## System Components

### 1. Backend Architecture
- **Framework**: FastAPI (Python 3.10+)
- **Concurrency Model**: Async/Await with ThreadPoolExecutor for blocking operations
- **Database**: SQLite (existing mtv_dl database integration)
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
  - Database initialization and connection management
  - Concurrent download handling with background tasks
  - REST API endpoints for frontend communication

- **Database Integration**: `mtv_dl/src/mtv_dl/mtv_dl.py`
  - Existing mtv_dl Database class for querying shows
  - Downloader class for downloading content

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
2. Download operations are submitted to a thread pool
3. Database operations remain synchronous but thread-safe
4. Status updates are managed with in-memory dictionary

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
- Multi-threading enhancements
- Database abstraction layer for future storage options
- Plugin architecture for additional download sources