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
- Series detection and handling
- Automatic season/episode organization
- Database update scheduling

### UI Components

#### 1. Search Interface

- Search for shows
- Add a show to the download queue
- Use the existing filter criteria of mtv_dl
- Support all filter operators: =, !=, +, -
- Support all filter fields: description, region, size, channel, topic, title, hash, url, duration, age, start, dow, hour, minute, season, episode
- Distinguish between normal shows and series
- Automatic season/episode detection and display

#### 2. Download Queue Interface
- Add new download tasks
- View active and queued downloads
- Pause/resume individual downloads
- Remove downloads from queue
- Progress indicators for downloads
- Status display (pending, downloading, completed, failed)
- Series-aware file organization

#### 3. Configuration Panel
- Query management (add/edit/remove monitoring queries)
- Download settings configuration
- Scheduler settings
- Database update configuration:
  - Cron-like expression for periodic database updates
  - Manual database update trigger
- Series handling configuration:
  - Enable/disable automatic series detection
  - Custom naming conventions for series vs normal shows
  - Season/episode folder structures
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
- Series detection and handling

### Phase 3: Advanced Features
- Multi-user support
- Enhanced notifications
- Performance monitoring
- Backup and restore functionality
- Full CLI parameter support
- Series-aware file organization and naming