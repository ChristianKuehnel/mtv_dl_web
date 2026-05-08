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
  - APScheduler crontab expression for periodic database updates
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

### Scheduler Cron Syntax

The scheduler must use APScheduler `CronTrigger.from_crontab()` syntax for all user-configured schedules.

Supported expression format:

```text
minute hour day_of_month month day_of_week
```

Examples:

```text
0 2 * * *        # Every day at 02:00
*/30 * * * *     # Every 30 minutes
15 6 * * mon-fri # Weekdays at 06:15
0 3 1 * *        # First day of every month at 03:00
```

Field ranges:

- `minute`: `0-59`
- `hour`: `0-23`
- `day_of_month`: `1-31`
- `month`: `1-12` or `jan-dec`
- `day_of_week`: `0-6` or `mon-sun`; APScheduler treats `0` as Monday and `6` as Sunday

Supported field operators:

- `*` for every value
- `,` for lists, such as `1,15,30`
- `-` for ranges, such as `mon-fri`
- `/` for steps, such as `*/15` or `1-23/2`

Unsupported schedule forms:

- Seconds or year fields
- Quartz-only syntax such as `?`, `L`, `W`, or `#`
- Shortcut aliases such as `@hourly`, `@daily`, or `@weekly`
- Per-expression timezone declarations; timezone is a separate application configuration value

Invalid expressions must be rejected in the UI and API with a clear validation message.

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
