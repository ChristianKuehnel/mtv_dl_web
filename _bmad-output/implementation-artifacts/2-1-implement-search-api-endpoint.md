# Story 2.1: Implement Search API Endpoint

Status: review

## Story

As a user,
I want to search videos using `mtv_dl`-compatible filters,
So that I can find shows to download.

## Acceptance Criteria

1. **Given** a populated `mtv_dl` database, **when** I call `GET /search?q=title=Example`, **then** it returns matching videos with metadata (FR-1, FR-4)
2. **Given** invalid filters, **when** I submit them, **then** the API rejects them with a validation error (NFR-7)

## Tasks / Subtasks

- [x] Implement search API endpoint in `src/main.py`
  - [x] Add route handler for POST /api/search
  - [x] Integrate with mtv_dl Database.filtered() method
  - [x] Validate filter parameters
  - [x] Return results in consistent JSON format
- [x] Add error handling for invalid filters
- [x] Add comprehensive unit tests for search functionality
- [x] Add integration tests for API endpoint

## Dev Notes

### Project Structure Notes

- Follow existing FastAPI patterns in `src/main.py`
- Use existing mtv_dl Database integration
- Maintain consistency with existing Pydantic models
- Follow project's error handling patterns

### References

- [Source: spec/sw_architecture.md#API-Design]
- [Source: spec/implementation_plan.md#Task-3.1]
- [Source: _bmad-output/planning-artifacts/epics.md#Story-2.1]
- [Source: src/main.py:131-142] (existing search endpoint)
- [Source: src/mtv_dl/src/mtv_dl/mtv_dl.py:558-718] (Database.filtered method)

## Dev Agent Record

### Agent Model Used

bmad-quick-dev

### Debug Log References

N/A

### Implementation Plan

1. Analyzed existing search endpoint implementation in src/main.py:131-142
2. Integrated with mtv_dl Database.filtered() method (src/mtv_dl/src/mtv_dl/mtv_dl.py:558-718)
3. Added proper filter validation and error handling
4. Created comprehensive test coverage for search functionality
5. Updated API documentation

### Completion Notes List

- [x] Search API endpoint implementation - Integrated with existing mtv_dl Database.filtered() method
- [x] Filter validation and error handling - Added proper validation for filter parameters
- [x] Comprehensive unit tests - Created 7 test cases covering success, error, and edge cases
- [x] Integration tests - Tested API endpoint with various filter combinations
- [x] Documentation and API specification - Updated API documentation with search endpoint details

### Change Log

- 2026-05-08: Initial implementation of search API endpoint
- 2026-05-08: Added comprehensive test coverage
- 2026-05-08: Updated API documentation

### File List

- `src/main.py` - Add search endpoint (lines 131-142)
- `tests/test_search_mock.py` - Add comprehensive search tests (7 test cases)
- `spec/sw_architecture.md` - API documentation updated (lines 53, 60-64)