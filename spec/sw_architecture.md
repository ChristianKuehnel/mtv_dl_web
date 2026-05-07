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
3. Status updates are managed with in-memory dictionary

## Deployment Architecture

### Single-User Focus
- Optimized for single-user experience
- No user authentication required
- Simple configuration with default paths

### Lightweight Design
- Minimal dependencies (FastAPI, SQLite, standard library)
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
- config files for local persistence
- Pydantic for data validation
- HTML/CSS/JS for frontend

### Testing Strategy
- Unit tests for individual components
- Integration tests for API endpoints
- Manual UI testing for frontend interaction
