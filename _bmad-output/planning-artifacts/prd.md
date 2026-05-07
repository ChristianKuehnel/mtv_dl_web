# MTV Downloader Web Interface - Product Requirements Document

## Executive Summary

This document outlines the product requirements for the MTV Downloader Web Interface, a graphical user interface equivalent to the existing CLI tool with added web-specific features like queuing, scheduling, and containerized deployment.

## Project Overview

**Project Name:** MTV Downloader Web Interface  
**Product Owner:** Christian  
**Release Version:** 1.0  
**Target Release Date:** TBA  

## Business Context

The MTV Downloader (mtv_dl) is a CLI tool for downloading videos from German public broadcasting services. This web interface aims to provide a graphical user interface equivalent to the existing CLI tool while adding web-specific features like queuing, scheduling, and containerized deployment.

## Key Features

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
- Search for shows with all filter criteria of mtv_dl
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
- Database update configuration with cron-like expression
- Series handling configuration with custom naming conventions
- All CLI options integrated with quality selection, target directory, subtitle/NFO handling, file modification time setting, series mode support, MKV merging support, post-download hooks, logging and verbosity options, database refresh settings

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

## Technical Requirements

### Web Framework
- FastAPI for API endpoint handling
- HTML/CSS/JS for frontend with Tailwind CSS CDN

### Database
- SQLite integration using existing mtv_dl Database class
- Persistent storage for configuration and download status

### Deployment
- Containerized deployment with Docker and Podman support
- Alpine Linux base image

## Success Metrics

### Functionality
- All CLI functionality available via web interface
- Queue management works with single-threaded processing
- Scheduler operates with configurable cron-like expressions
- All filter operators and fields supported

### Performance
- Fast search and filtering operations
- Concurrent download processing
- Efficient resource utilization

### Usability
- Intuitive user interface
- Responsive design for all screen sizes
- Clear status indicators for downloads and queues

## Risks and Mitigations

### Technical Risks
- Integration complexity with existing mtv_dl codebase
- Performance limitations of single-threaded download processing

### Mitigation Strategies
- Careful integration of mtv_dl modules without reimplementing logic
- Performance testing during development phases

## Acceptance Criteria

1. Web interface functional and responsive
2. All search filters work as expected
3. Download queue management works correctly
4. Scheduler executes queries according to schedule
5. Container deployment works without issues
6. All existing mtv_dl CLI features available via web interface