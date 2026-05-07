# MTV Downloader Web Interface - Implementation Plan

## Definition of Done
Before each task is considered complete, the following criteria must be met:
- Functionality covered by unit tests, all tests must be passing
- Use black for Python code formatting
- Add HTML and JS code formatting using Prettier 
- Use Python type checking with mypy for validation
- Use hadolint as formatter and linter for Docker files
- Use ShellCheck as linter for shell scripts
- @scripts/linting.sh must pass and changes were committed to git
- Add smoke test to check if the backend starts and health check returns 200 OK
- Add smoke test to deploy the container using Podman and verify health check

## Phase 1: Basic Web Interface & Containerization

### Task 1.1: Create Hello World Web UI
- Create basic HTML/CSS/JS frontend with simple "Hello World" interface
- Implement a basic FastAPI backend that serves the frontend and responds to health checks
- Add basic container configuration using Alpine Linux base image
- Configure Dockerfile with proper entrypoint and port exposure

### Task 1.2: Containerization & Smoke Tests
- Build container image using Alpine Linux
- Create docker-compose.yml for local development
- Implement smoke tests to verify:
  - Container starts successfully
  - Web interface responds on configured port
  - Health endpoint returns 200 OK
  - No crashes on startup
- Test deployment with Podman

### Task 1.3: Basic Container Configuration
- Set up volume mounts for persistent data storage
- Configure environment variables for port configuration
- Create sample configuration file structure
- Test container persistence with database restarts

## Phase 2: MTV DL Integration & Database Management

### Task 2.1: Integrate MTV DL Backend
- Import and integrate existing mtv_dl Python modules into backend
- Implement database initialization and connection management
- Create API endpoint for database updates
- Set up proper error handling for database operations

### Task 2.2: Database Persistence
- Configure persistent storage for database files in /data directory
- Implement database backup/restore mechanisms
- Add configuration option for database path
- Test that database survives container restarts

### Task 2.3: Database Update Button
- Add "Update Database" button to frontend
- Implement API endpoint to trigger database refresh
- Add visual feedback during database update process
- Test database update functionality

## Phase 3: Search Functionality

### Task 3.1: Search API Implementation
- Implement search endpoint that accepts filter parameters
- Integrate mtv_dl filtering logic
- Handle all filter operators (=, !=, +, -) and fields
- Return search results in consistent JSON format

### Task 3.2: Search UI Implementation
- Create search form with filter input fields
- Implement result display matching CLI layout
- Add selection capability for shows
- Handle empty search results gracefully
- No pagination required - show all results

### Task 3.3: UI Enhancement
- Style search results to resemble CLI output format
- Add visual indication of show properties (duration, size, etc.)
- Implement responsive design for all screen sizes
- Add loading indicators during search operations

## Phase 4: Download Functionality

### Task 4.1: Single Download Implementation
- Implement download endpoint for single show downloads
- Create download button for selected shows
- Set up background download processing with threading
- Implement download status tracking
- Handle download progress reporting

### Task 4.2: Download Limitation
- Restrict to single download at a time
- Implement download queue management
- Add visual indicators for active downloads
- Handle download completion and failure states

## Phase 5: Download Queue Management

### Task 5.1: Queue Implementation
- Create download queue data structure
- Implement queue management API endpoints
- Add ability to add shows to queue
- Implement queue processing logic (one at a time)

### Task 5.2: Queue UI Controls
- Add "Add to Queue" buttons for shows
- Create queue display showing pending downloads
- Implement queue controls (pause/resume/clear)
- Show download progress for queued items
- Add visual distinction between queued and active downloads

## Phase 6: Scheduling Feature

### Task 6.1: Scheduler Implementation
- Implement background scheduler service
- Create API endpoints for query management
- Add cron-like expression configuration
- Implement periodic database checking and query execution

### Task 6.2: Scheduling UI
- Create configuration panel for scheduling
- Add form for adding new scheduled queries
- Implement UI for viewing and managing scheduled jobs
- Add ability to trigger manual database updates
- Test scheduler functionality with different cron expressions

### Task 6.3: Job Management
- Store scheduled queries in persistent configuration
- Create job execution history tracking
- Add error handling for failed scheduled jobs
- Implement retry mechanisms for failed jobs