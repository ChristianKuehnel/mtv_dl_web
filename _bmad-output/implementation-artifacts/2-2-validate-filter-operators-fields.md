# Story 2.2: Validate Filter Operators/Fields

Status: review

## Story

As a user,
I want to use filter operators (`=`, `!=`, `+`, `-`) and fields (`title`, `channel`, etc.),
So that I can refine my searches.

## Acceptance Criteria

1. **Given** valid operators/fields, **when** I submit a search, **then** the API processes them correctly (FR-2, FR-3)
2. **Given** unsupported operators/fields, **when** I submit them, **then** the API returns a `400 Bad Request` (NFR-1)

## Tasks / Subtasks

- [x] Implement filter validation in search API endpoint
  - [x] Add validation for supported operators (=, !=, +, -)
  - [x] Add validation for supported fields (description, region, size, channel, topic, title, hash, url, duration, age, start, dow, hour, minute, season, episode)
  - [x] Return 400 Bad Request for invalid operators/fields
- [x] Add comprehensive unit tests for filter validation
  - [x] Test valid operator combinations
  - [x] Test invalid operator rejection
  - [x] Test valid field combinations
  - [x] Test invalid field rejection
- [x] Add integration tests for API endpoint validation
  - [x] Test successful validation with valid filters
  - [x] Test error responses with invalid filters

## Dev Notes

### Project Structure Notes

- Follow existing FastAPI patterns in `src/mtv_dl_web/main.py`
- Use existing mtv_dl Database integration
- Maintain consistency with existing Pydantic models
- Follow project's error handling patterns

### Filter Specification

**Supported Operators:**
- `=` (equals)
- `!=` (not equals)
- `+` (contains)
- `-` (excludes)

**Supported Fields:**
- `description`
- `region`
- `size`
- `channel`
- `topic`
- `title`
- `hash`
- `url`
- `duration`
- `age`
- `start`
- `dow` (day of week)
- `hour`
- `minute`
- `season`
- `episode`

### References

- [Source: spec/sw_architecture.md#API-Design]
- [Source: spec/implementation_plan.md#Task-3.2]
- [Source: _bmad-output/planning-artifacts/epics.md#Story-2.2]
- [Source: src/mtv_dl_web/main.py:131-142] (existing search endpoint)
- [Source: src/mtv_dl/src/mtv_dl/mtv_dl.py:558-718] (Database.filtered method)

## Dev Agent Record

### Agent Model Used

bmad-dev-story

### Debug Log References

N/A

### Implementation Plan

1. Analyze existing search endpoint implementation in src/mtv_dl_web/main.py:131-142
2. Add filter validation logic for operators and fields
3. Implement proper error handling for invalid filters
4. Create comprehensive test coverage for validation
5. Update API documentation

### Completion Notes List

- [x] Filter validation implementation - Added validation for operators and fields
- [x] Error handling - Returns 400 Bad Request for invalid filters
- [x] Comprehensive unit tests - Created 11 test cases covering validation scenarios
- [x] Integration tests - Tested API endpoint with various filter combinations
- [x] Documentation and API specification - Updated API documentation

### Change Log

- 2026-05-08: Initial implementation of filter validation
- 2026-05-08: Added comprehensive test coverage
- 2026-05-08: Updated API documentation

### File List

- `src/mtv_dl_web/main.py` - Added filter validation function and updated search endpoint (lines 100-160)
- `tests/test_filter_validation.py` - Added comprehensive validation tests (11 test cases)
- `spec/sw_architecture.md` - API documentation updated with filter validation details
