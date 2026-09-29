---
id: TASK-7.3
title: Add API tests for the spots endpoint
status: Done
assignee:
  - '@qwen'
created_date: '2026-09-29 11:09'
updated_date: '2026-09-29 12:33'
labels:
  - backend
  - api
  - tests
dependencies: []
parent_task_id: TASK-7
priority: medium
type: task
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Cover /api/spots/ (ParkingSpotViewSet, full CRUD). The endpoint manages parking spots identified by level and number with a spot type. Tests should hit the real HTTP layer via the DRF test client. Keep the module to at most 5 tests focused on the most important behaviors.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Creating a spot with a valid level, number, and spot type returns 201 and the created representation
- [x] #2 Listing and retrieving spots returns the persisted records
- [x] #3 A duplicate level and number pair is rejected with 400
- [x] #4 Invalid spot type or missing fields are rejected with 400
- [x] #5 The module contains no more than 5 tests
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add src/parking/tests/test_api_spots.py following the conventions of test_api_customers.py and test_api_vehicles.py (APITestCase, shared fixture base class, one test class per behavior).
2. Write exactly 4 tests: (a) POST valid spot -> 201 with created representation and persisted row; (b) GET list + retrieve returns persisted records; (c) POST duplicate (level, number) -> 400 with no new row; (d) POST invalid spot_type and missing fields -> 400 with no new rows.
3. Keep the module at or under 5 tests (AC #5).
4. Run 'uv run python manage.py test parking.tests.test_api_spots' from src/ and confirm all tests pass, then run the full suite.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created src/parking/tests/test_api_spots.py (via subagent) with exactly 4 tests: create 201 + representation, list/retrieve, duplicate (level, number) 400, invalid spot_type/missing fields 400. Targeted run: 4/4 OK. Full suite: 159/159 OK.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added src/parking/tests/test_api_spots.py covering /api/spots/ via the DRF test client: valid create (201 + representation), list/retrieve of persisted records, duplicate (level, number) rejection (400), and invalid spot_type/missing fields rejection (400). Module contains exactly 4 tests, within the 5-test limit. Verified with 'uv run python manage.py test' from src/: targeted run 4/4 OK, full suite 159/159 OK.
<!-- SECTION:FINAL_SUMMARY:END -->
