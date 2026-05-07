---
project_name: 'mtv_dl_web'
user_name: 'Christian'
date: '2026-05-07'
stepsCompleted: ['step-1-validate-prerequisites', 'step-2-design-epics']
inputDocuments: ['_bmad-output/planning-artifacts/prd.md']
fr_list: |
  FR1: The system shall provide a web interface for downloading videos from German public broadcasting services
  FR2: The system shall support searching for shows using all filter criteria of mtv_dl
  FR3: The system shall support all filter operators: =, !=, +, -
  FR4: The system shall support all filter fields: description, region, size, channel, topic, title, hash, url, duration, age, start, dow, hour, minute, season, episode
  FR5: The system shall distinguish between normal shows and series
  FR6: The system shall support automatic season/episode detection and display
  FR7: The system shall provide a download management interface
  FR8: The system shall support queue management for sequential downloads
  FR9: The system shall support background processing of downloads
  FR10: The system shall provide a scheduler for monitoring and downloading new episodes
  FR11: The system shall support self-hosted containerized deployment
  FR12: The system shall allow adding shows to download queue
  FR13: The system shall integrate full CLI functionality with web interface
  FR14: The system shall support series detection and handling
  FR15: The system shall provide automatic season/episode organization
  FR16: The system shall support database update scheduling
  FR17: The system shall provide a search interface with filter criteria
  FR18: The system shall provide a download queue interface
  FR19: The system shall provide a configuration panel
  FR20: The system shall support query management (add/edit/remove monitoring queries)
  FR21: The system shall support download settings configuration
  FR22: The system shall support scheduler settings
  FR23: The system shall support database update configuration with cron-like expression
  FR24: The system shall support series handling configuration with custom naming conventions
  FR25: The system shall integrate all CLI options with quality selection, target directory, subtitle/NFO handling, file modification time setting, series mode support, MKV merging support, post-download hooks, logging and verbosity options, database refresh settings
nfr_list: |
  NFR1: The system shall be responsive and accessible on all modern browsers
  NFR2: The system shall support single-user access without authentication
  NFR3: The system shall maintain performance with large search results
  NFR4: The system shall provide clear status indicators for downloads and queues
  NFR5: The system shall be designed for containerized deployment
  NFR6: The system shall maintain data integrity during concurrent operations
  NFR7: The system shall preserve existing mtv_dl configuration files
  NFR8: The system shall comply with the MIT license requirements
additional_requirements: |
  - Use existing mtv_dl Database class for SQLite integration
  - Use existing mtv_dl Downloader class for download processing
  - Implement FastAPI with Python 3.10+
  - Use HTML/CSS/JS frontend with Tailwind CSS CDN
  - Support containerized deployment with Docker and Podman
  - Use Alpine Linux base image for container deployment
  - Implement single-threaded download processing to match existing mtv_dl logic
  - Single-user focus with no authentication required
  - Use yaml config files for service configuration, do not create another database
ux_design_requirements: |
  UX-DR1: Implement a responsive UI design using Tailwind CSS CDN
  UX-DR2: Create intuitive search interface with filter controls
  UX-DR3: Design download queue interface with status indicators
  UX-DR4: Create configuration panel with form elements for settings
  UX-DR5: Ensure all UI components are accessible and keyboard navigable
  UX-DR6: Implement clear visual hierarchy for user actions and status updates
---