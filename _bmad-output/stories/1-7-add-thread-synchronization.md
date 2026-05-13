# Story: Add thread synchronization to active_downloads dictionary access

## User Story
As a self-hosting user, I want the MTV Downloader web interface to protect active download status updates so that concurrent requests and background work do not cause race conditions or data corruption (NFR-20).

## Acceptance Criteria

### Scenario: Concurrent access to active_downloads dictionary
Given multiple background download tasks are running simultaneously
And each task tries to update the status of a download
When the tasks execute concurrently
Then the application should not crash or corrupt data
And all download statuses should be properly recorded

### Scenario: Concurrent status queries and updates
Given the web interface has active downloads
And multiple users are viewing download status simultaneously
And background download tasks are updating statuses
When requests are processed concurrently
Then all status queries should return consistent data
And no race conditions should occur

### Scenario: Safe shutdown with active downloads
Given there are active downloads running
When the application is shut down gracefully
Then all active downloads should be safely managed
And no data corruption should occur during shutdown

## Technical Requirements

### Problem Statement
The `active_downloads` dictionary is accessed and modified from:
- Main thread (start_download function)  
- Background threads (download_show_background function)
- API endpoints (get_download_status and get_all_download_statuses)

No locking mechanism protects this shared state, leading to potential race conditions where multiple threads could read/write simultaneously, resulting in inconsistent state or crashes.

### Implementation Approach
1. Add threading locks to protect access to the `active_downloads` dictionary
2. Implement thread-safe read/write operations for the dictionary
3. Ensure all access points synchronize properly before accessing shared state
4. Maintain backward compatibility with existing API contract

### Code Changes Required
- Add `threading.RLock()` for protecting `active_downloads` dictionary access
- Modify all functions accessing `active_downloads` to use the lock
- Update status update and retrieval operations to be thread-safe

## Architecture Compliance

### Location of Changes
- File: `src/mtv_dl_web/main.py`
- Functions affected:
  - `start_download` (sets initial status)
  - `download_show_background` (updates status)
  - `get_download_status` (reads status)
  - `get_all_download_statuses` (reads all statuses)

### Design Pattern
Following the existing pattern of using locks for shared mutable state:
- Similar to existing `database_update_lock` pattern already used in the codebase
- Using `threading.RLock()` for reentrant locking capability
- Consistent with Python threading best practices

## Testing Requirements

### Unit Testing
- Test concurrent access to `active_downloads` with multiple threads
- Verify no race conditions occur during simultaneous read/write operations
- Test status updates are preserved correctly

### Integration Testing
- Simulate multiple concurrent download tasks
- Verify status consistency across concurrent API requests
- Test end-to-end scenario with actual download simulations

### Performance Testing
- Measure performance impact of added locking
- Ensure locking doesn't introduce significant latency
- Verify system remains responsive under concurrent load

## Developer Context and Guardrails

### Current State Analysis
The existing codebase has several global variables that are not thread-safe:
- `active_downloads: dict[str, dict[str, Any]] = {}` (line 65)
- These variables are accessed from multiple threads without synchronization

### Risk Mitigation
- The change preserves all existing functionality
- Minimal performance impact expected
- Existing API contracts remain unchanged
- Follows established patterns already in the codebase

### Implementation Notes
1. Use `threading.RLock()` which allows the same thread to acquire the lock multiple times
2. Apply lock acquisition at the beginning of each access point
3. Release lock in finally block or use context manager pattern
4. Maintain the same data structures and interfaces

### Dependencies
- No new dependencies required
- Built-in Python `threading` module sufficient
- Existing architecture patterns fully compatible

## Dev Agent Record

### Implementation Plan

1. Added `threading.RLock()` for protecting `active_downloads` dictionary access
2. Modified all functions accessing `active_downloads` to use the lock:
   - `start_download` (sets initial status)
   - `download_show_background` (updates status)
   - `get_download_status` (reads status)
   - `get_all_download_statuses` (reads all statuses)
3. Ensured all access points synchronize properly before accessing shared state
4. Maintained backward compatibility with existing API contract

### Completion Notes List

- [x] Added threading.RLock() for protecting active_downloads dictionary access
- [x] Modified start_download function to use the lock when setting initial status
- [x] Modified download_show_background function to use the lock when updating status
- [x] Modified get_download_status function to use the lock when reading status
- [x] Modified get_all_download_statuses function to use the lock when reading all statuses
- [x] All functions protect access to active_downloads with the new lock
- [x] Preserved all existing functionality and API contracts
- [x] Followed established patterns already in the codebase (similar to database_update_lock)

## Completion Status
- [x] Analysis complete
- [x] Implementation planned
- [x] Code changes implemented
- [ ] Tests written and passing
- [ ] Documentation updated