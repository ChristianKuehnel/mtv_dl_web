# MTV Downloader Web Interface

A lightweight web interface for the MediathekView Downloader with Python backend supporting concurrent web requests and downloads.

## Quick Start

### 1. Development - Local Shell

```bash
# Install dependencies
uv sync

# Start the development server
uv run src/main.py

# The service will be available at http://localhost:8000
```

### 2. Production - Docker Container

#### Option A: Using Docker Compose (Recommended)

```bash
# Start the service with Docker Compose (includes volume mounting)
docker-compose up -d

# The service will be available at http://localhost:8000
# Volumes will be created in:
# - ./data - Application data
# - ./downloads - Download storage
# - ./config - Configuration files
# - ./.mtv_dl_web - Database files (including filmliste.sqlite)
```

#### Option B: Using Docker Directly

```bash
# Build the container image
docker build -t mtv-dl-web .

# Create directories for volume mounting
mkdir -p ./data ./downloads ./config

# Run the container with volume mounts
docker run -d -p 8000:8000 \
  -v $(pwd)/data:/data \
  -v $(pwd)/downloads:/downloads \
  -v $(pwd)/config:/config \
  -v $(pwd)/.mtv_dl_web:/home/appuser/.mtv_dl_web \
  --name mtv-dl-web \
  mtv-dl-web

# The service will be available at http://localhost:8000
```

#### Volume Persistence

The container uses the following volume mounts for data persistence:
- `/data` - Application data storage
- `/downloads` - Downloaded video files
- `/config` - Configuration files
- `/home/appuser/.mtv_dl_web` - Database files (filmliste.sqlite)

All volumes are configured to persist across container restarts.

## API Endpoints

- **GET /** - Main HTML interface
- **GET /health** - Health check endpoint
- **POST /api/search** - Search for shows with filters
- **POST /api/download** - Initiate downloads
- **GET /api/download/status/{download_id}** - Get download status
- **GET /api/download/status** - Get all download statuses

## Configuration

The service uses the following environment variables:

- `PORT` - Service port (default: 8000)
- `DATABASE_DIR` - Database directory (default: ~/.mtv_dl_web)
- `LOG_LEVEL` - Logging level (default: INFO)

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_search.py
```

### Code Quality

```bash
# Run linting
black src/ tests/

# Run type checking
mypy src/ tests/
```

## Deployment

### Docker

```bash
# Build and run with Docker
docker build -t mtv-dl-web .
docker run -d -p 8000:8000 --name mtv-dl-web mtv-dl-web
```

### Podman

```bash
# Build and run with Podman
podman build -t mtv-dl-web .
podman run -d -p 8000:8000 --name mtv-dl-web mtv-dl-web
```

## Architecture

- **Backend:** FastAPI (Python 3.10+)
- **Frontend:** Pure HTML/CSS/JavaScript with Tailwind CSS
- **Database:** SQLite via mtv_dl integration
- **Concurrency:** Async/Await with ThreadPoolExecutor

## License

MIT License - See LICENSE file for details.