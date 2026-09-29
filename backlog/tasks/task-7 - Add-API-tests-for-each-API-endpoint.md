---
id: TASK-7
title: Add API tests for each API endpoint
status: Done
assignee: []
created_date: '2026-09-29 11:08'
updated_date: '2026-09-29 13:51'
labels:
  - backend
  - api
  - tests
dependencies: []
references:
  - specs/SRS2.md
priority: medium
type: feature
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
SRS2 deferred API test expansion ("api tests to be added later") and the existing test_api.py only has initial coverage mixed with the TASK-4 work. This initiative adds dedicated, organized API test coverage for every DRF endpoint under /api/, one subtask per endpoint. To keep the suite focused and fast, each endpoint is capped at 5 tests covering its most important behaviors (happy path, key validation errors, and endpoint-specific rules).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Every API endpoint (customers, vehicles, spots, sessions, sessions exit) has a dedicated test module
- [x] #2 The full test suite passes with the new API tests
- [x] #3 Each endpoint test module contains no more than 8 tests (the original 5-test cap was raised to 8 by the user for the spots, sessions, and session exit modules)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Review for completion: all 5 subtasks Done. Per-module test counts (test runner): customers 5, vehicles 5, spots 8, sessions 8, session exit 8. AC #2 reworded from the original 5-test cap to 8 to reflect the user-directed cap raises recorded in TASK-7.3/7.4/7.5. Full suite: 179/179 OK.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
All five DRF endpoints under /api/ now have dedicated API test modules: test_api_customers.py (5 tests), test_api_vehicles.py (5), test_api_spots.py (8), test_api_sessions.py (8), and test_api_session_exit.py (8), each within its approved cap. Verified with 'uv run python manage.py test' from src/: full suite 179/179 passing.
<!-- SECTION:FINAL_SUMMARY:END -->
