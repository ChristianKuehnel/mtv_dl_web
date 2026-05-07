# MTV Downloader Web Interface - Product Design Document

## Overview
This document outlines the design for a web interface for the MTV Downloader (mtv_dl) that provides a graphical user interface equivalent to the existing CLI tool while adding web-specific features like queuing, scheduling, and containerized deployment.

## Features

### Core Functionality
- Download management interface
- Queue management for sequential downloads
- Background processing of downloads
- Scheduler for monitoring and downloading new episodes
- Self-hosted containerized deployment
- Searching for shows
- Adding shows to download queue
- Full CLI functionality integration

### UI Components

#### 1. Search Interface

- Search for shows
- Add a show to the download queue
- Use the existing filter criteria of mtv_dl
- Support all filter operators: =, !=, +, -
- Support all filter fields: description, region, size, channel, topic, title, hash, url, duration, age, start, dow, hour, minute, season, episode

#### 2. Download Queue Interface
- Add new download tasks
- View active and queued downloads
- Pause/resume individual downloads
- Remove downloads from queue
- Progress indicators for downloads
- Status display (pending, downloading, completed, failed)

#### 3. Configuration Panel
- Query management (add/edit/remove monitoring queries)
- Download settings configuration
- Scheduler settings
- All CLI options integrated:
  - Quality selection (high, low, default)
  - Target directory configuration
  - Subtitle and NFO file handling
  - File modification time setting
  - Series mode support
  - MKV merging support
  - Post-download hooks
  - Logging and verbosity options
  - Database refresh settings

## Implementation Plan

### Phase 1: Basic Web Interface
- Simple web UI with download form
- Queue management with single-threaded processing
- Basic configuration panel
- Search interface with all filter capabilities

### Phase 2: Scheduling & Monitoring
- Scheduler implementation
- Query monitoring logic
- Duplicate detection logic
- Integration with mtv_dl CLI arguments

### Phase 3: Advanced Features
- Multi-user support
- Enhanced notifications
- Performance monitoring
- Backup and restore functionality
- Full CLI parameter support

## Technology Stack

### Frontend
- React.js with Material UI components
- Responsive design for desktop and mobile

### Backend
- Node.js with Express.js
- SQLite for local storage
- BullMQ for job queue management

### Infrastructure
- Docker containerization
- NGINX reverse proxy
- PM2 for process management

## Data Flow

1. User adds download query through web UI
2. Query stored in database
3. Job placed in download queue
4. Job processor picks up queued item (single-threaded)
5. CLI tool invoked for actual download
6. Download status updates stored and reflected in UI
7. Scheduler periodically checks configured queries
8. New episodes detected and added to download queue

## Deployment Requirements

### Container Configuration
- Base image: node:alpine
- Expose port 3000
- Mount volume for persistent data
- Environment variables for configuration
- Health check endpoint

### Security Considerations
- Input validation for all user inputs
- Sanitization of CLI arguments
- Authentication for admin access
- Secure storage of sensitive configuration

## Future Enhancements
- Webhooks for external notifications
- Integration with media servers
- Cloud storage integration
- Mobile app companion

## CLI Command Line Arguments Integration

### Main Commands
- `list`: Show query results as ASCII table
- `dump`: Show query results as JSON list
- `download`: Download shows in query results
- `history`: Show list of downloaded shows

### Common Options Across Commands
- `--config`/`-c`: YAML config file for overriding arguments
- `--include-future`: Include shows that have not yet started
- `--sets`/`-s`: File to load different sets of filters
- `--count`/`-c`: Limit number of results (for list command)
- `--verbose`/`-v`: Show more details
- `--quiet`/`-q`: Hide everything not really needed
- `--no-bar`/`-b`: Hide the progress bar
- `--logfile`/`-l`: Log messages to a file instead of stdout
- `--certifi`: Use certifi instead of builtin SSL certificates
- `--dir`/`-d`: Directory to put databases in
- `--refresh-after`/`-r`: Update database if older than given hours

### List/Dump Command Filters
- Filter arguments with operators: =, !=, +, -
- Supported fields: description, region, size, channel, topic, title, hash, url, duration, age, start, dow, hour, minute, season, episode
- Multiple filters can be combined

### Download Command Options
- `--high`/`-h`: Download best available version
- `--low`/`-l`: Download smallest available version
- `--oblivious`/`-o`: Download even if show already marked as downloaded
- `--target`/`-t`: Directory to put downloaded files in
- `--mark-only`: Do not download, just mark as downloaded
- `--strm`: Create .strm files instead of downloading media
- `--no-subtitles`: Do not try to download subtitles
- `--no-nfo`: Do not create nfo files
- `--set-file-mod-time`: Set file modification time to aired date
- `--series`: Mark show as series in nfo file
- `--mkvmerge`/`-m`: Convert downloads to MKV containers using mkvmerge
- `--post-download`: Program to run after download finishes