## Deferred from: code review of 1-9-concurrency-improvements.md (2026-05-13)

- Exception cleanup test may not mutate shared module state due to local variable shadowing (`tests/test_concurrent_access_stress.py:198`).
- Lock-order invariant is documented, but opposite lock-acquisition/deadlock path is not evidenced as tested (`tests/test_concurrent_access_stress.py:154`).
