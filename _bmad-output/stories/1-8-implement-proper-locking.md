# Story: Implement proper locking for all shared mutable state

## User Story
As a self-hosting user, I want the MTV Downloader web interface to protect all shared mutable state so that the application remains stable and data integrity is maintained under concurrent usage (NFR-20).

## Acceptance Criteria

### Scenario: Multiple shared data structures concurrent access
Given the application has multiple shared mutable state variables
When multiple threads access these variables simultaneously
Then all shared state should be protected from race conditions
And data integrity should be maintained

### Scenario: Database refresh and download operations concurrency
Given database refresh is happening in background
And download operations are running simultaneously
When both operations access shared resources
Then no conflicts should occur
And both operations should complete successfully

### Scenario: Thread-safe global variable access
Given global variables that store application state
When multiple threads modify these variables
Then all modifications should be atomic and consistent
And no partial updates should occur

## Technical Requirements

### Problem Statement
The application has several global variables that are modified by multiple threads without proper synchronization:
- `download_queue: list[dict[str, Any]] = []` (line 63)
- `active_downloads: dict[str, dict[str, Any]] = {}` (line 65) 
- `database_update_lock` (line 66) and `_database_update_count` (line 67)
- `database_refresh_lock` (line 70) and related refresh state variables

While some state is partially protected, the overall design lacks comprehensive thread safety.

### Implementation Approach
1. Add comprehensive thread synchronization for all shared mutable state
2. Implement consistent locking strategy throughout the application
3. Ensure all access points to shared variables are properly synchronized
4. Maintain performance by minimizing lock scope and duration

### Code Changes Required
1. Add lock for `download_queue` operations (when needed)
2. Add comprehensive lock for `active_downloads` operations (already covered in Story 1.7)
3. Ensure all global state access follows consistent locking patterns
4. Review and potentially consolidate locking mechanisms

## Architecture Compliance

### Location of Changes
- File: `src/mtv_dl_web/main.py`
- All global variables and shared state access points

### Design Patterns
Following established patterns from the codebase:
- Using `threading.RLock()` for mutual exclusion
- Consistent lock acquisition/release pattern
- Minimizing lock scope to reduce contention
- Maintaining existing code structure and API contracts

### Performance Considerations
- Locks should be held for minimal time
- Avoid holding locks during I/O operations
- Consider using lock-free data structures where appropriate

## Testing Requirements

### Unit Testing
- Test all global variable access patterns for thread safety
- Create stress tests with multiple concurrent threads
- Verify no deadlocks or race conditions in shared state operations

### Integration Testing
- Test realistic concurrent usage scenarios
- Verify database refresh and download operations can run simultaneously
- Confirm all API endpoints work reliably under concurrent load

### Regression Testing
- Ensure existing functionality remains intact
- Verify no performance degradation
- Confirm no breaking changes to API contracts

## Developer Context and Guardrails

### Current State Analysis
The current state shows a mixed approach to thread safety:
- Some global variables are guarded (database_update_lock)
- Others are not (download_queue, active_downloads)
- Inconsistent locking patterns across the codebase

### Risk Mitigation
- Focus on minimum necessary changes to achieve thread safety
- Preserve all existing functionality and behavior
- Use proven Python threading patterns
- Ensure backward compatibility

### Implementation Notes
1. For `download_queue`, determine if synchronization is actually needed based on usage patterns
2. Apply consistent locking approach to all shared mutable state
3. Use context managers for automatic lock cleanup
4. Consider if some global variables can be replaced with thread-local storage or immutable patterns

### Dependencies
- No new dependencies required
- Built-in Python `threading` module sufficient
- Existing architecture patterns fully compatible

## Completion Status
- [x] Analysis complete
- [x] Implementation planned
- [x] Code changes implemented
- [ ] Tests written and passing
- [ ] Documentation updated

### Review Findings
- [x] [Review][Dismiss] Define DELETE semantics for active downloads — resolved by user decision: DELETE is status-only and running jobs may continue.
- [x] [Review][Dismiss] Confirm idempotency contract for repeated DELETE calls — resolved by user decision: keep current `404` behavior for already-absent items.
- [x] [Review][Patch] Replace blocking lock usage in async endpoint with non-blocking-safe synchronization strategy [src/mtv_dl_web/main.py:573]
- [x] [Review][Patch] Apply `download_queue_lock` at all `download_queue` read/write access points (or remove unused lock if intentionally out of scope) [src/mtv_dl_web/main.py:57]
- [x] [Review][Patch] Bring implementation in line with story acceptance scope before marking completion checkboxes as done [src/mtv_dl_web/main.py:573]
- [x] [Review][Defer] Establish and document global lock acquisition order across shared-state locks [src/mtv_dl_web/main.py:57] — deferred, pre-existing
