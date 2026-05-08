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

### 2. Production - Podman Container

```bash
# Build the container image
podman build -t mtv-dl-web .

# Run the container
podman run -d -p 8000:8000 --name mtv-dl-web mtv-dl-web

# The service will be available at http://localhost:8000
```

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