---
id: TASK-7.2
title: Add API tests for the vehicles endpoint
status: Done
assignee:
  - '@Qwen'
created_date: '2026-09-29 11:09'
updated_date: '2026-09-29 13:47'
labels:
  - backend
  - api
  - tests
dependencies: []
parent_task_id: TASK-7
priority: medium
type: task
ordinal: 25000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Cover /api/vehicles/ (VehicleViewSet, full CRUD). The endpoint manages registrations, vehicle types, and the optional customer owner. Tests should hit the real HTTP layer via the DRF test client. Keep the module to at most 5 tests focused on the most important behaviors.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Creating a vehicle with a valid type and optional customer returns 201 and the created representation
- [x] #2 Listing and retrieving vehicles returns the persisted records
- [x] #3 Duplicate registration is rejected with 400
- [x] #4 Invalid vehicle type or unknown customer is rejected with 400
- [x] #5 The module contains no more than 5 tests
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create a new dedicated test module src/parking/tests/test_api_vehicles.py (do not modify existing test files) with at most 5 tests for /api/vehicles/ covering: create 201 with valid type and optional customer, list/retrieve, duplicate registration 400, invalid vehicle type or unknown customer 400. 2. Run the new module and the full suite via uv run python manage.py test. 3. Verify each acceptance criterion against the test results.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
You are implementing backlog task TASK-7.2: "Add API tests for the vehicles endpoint" for the Django REST Framework project in /workspace/smart-parking-lot-v2 (Python project root: /workspace/smart-parking-lot-v2/src).

Goal: add a NEW dedicated API test module for the /api/vehicles/ endpoint (VehicleViewSet, full CRUD). Do NOT modify or reuse any existing test file — create a brand new file:

  src/parking/tests/test_api_vehicles.py

Requirements:
1. First read for conventions (do not modify them):
   - src/parking/tests/test_api_customers.py  (the most recent dedicated endpoint test module; follow its style)
   - src/parking/tests/test_api.py  (existing API test style/fixtures)
   - src/parking/views.py, src/parking/serializers.py, src/parking/models.py
2. Write at most 5 tests in the new module, hitting the real HTTP layer with the DRF test client (rest_framework.test.APIClient / APITestCase), covering:
   - Creating a vehicle with a valid vehicle_type (e.g. "car") and an optional customer returns 201 and the created representation (id, registration, vehicle_type, customer, created_at, updated_at); also verify a vehicle created without a customer is accepted.
   - Listing and retrieving vehicles returns the persisted records.
   - Creating a vehicle with a duplicate registration is rejected with 400 and no second row is created.
   - Invalid vehicle_type (e.g. "truck") or an unknown customer id is rejected with 400.
   You may combine list+retrieve, or the two 400 cases, within a single test to stay within the 5-test cap.
3. Follow the existing test conventions (APITestCase, shared base class with setUp fixtures, status.HTTP_* constants, format="json", test_* naming, module docstring).
4. Run the new module, then the full suite, from the src/ directory:
     cd /workspace/smart-parking-lot-v2/src && uv run python manage.py test parking.tests.test_api_vehicles
     cd /workspace/smart-parking-lot-v2/src && uv run python manage.py test
5. If a test fails because of a genuine application bug (not a test bug), do NOT change application code — stop and report the bug.

Report back: the exact file created, the list of test method names, the number of tests in the module, and the full pass/fail summary of both test runs.

----

You are implementing backlog task TASK-7.2: "Add API tests for the vehicles endpoint" for the Django REST Framework project in /workspace/smart-parking-lot-v2 (Python project root: /workspace/smart-parking-lot-v2/src).

Goal: add a NEW dedicated API test module for the /api/vehicles/ endpoint (VehicleViewSet, full CRUD). Do NOT modify or reuse any existing test file — create a brand new file:

  src/parking/tests/test_api_vehicles.py

Requirements:
1. First read for conventions (do not modify them):
   - src/parking/tests/test_api_customers.py  (the most recent dedicated endpoint test module; follow its style)
   - src/parking/tests/test_api.py  (existing API test style/fixtures)
   - src/parking/views.py, src/parking/serializers.py, src/parking/models.py
2. Write at most 5 tests in the new module, hitting the real HTTP layer with the DRF test client (rest_framework.test.APIClient / APITestCase), covering:
   - Creating a vehicle with a valid vehicle_type (e.g. "car") and an optional customer returns 201 and the created representation (id, registration, vehicle_type, customer, created_at, updated_at); also verify a vehicle created without a customer is accepted.
   - Listing and retrieving vehicles returns the persisted records.
   - Creating a vehicle with a duplicate registration is rejected with 400 and no second row is created.
   - Invalid vehicle_type (e.g. "truck") or an unknown customer id is rejected with 400.
   You may combine list+retrieve, or the two 400 cases, within a single test to stay within the 5-test cap.
3. Follow the existing test conventions (APITestCase, shared base class with setUp fixtures, status.HTTP_* constants, format="json", test_* naming, module docstring).
4. Run the new module, then the full suite, from the src/ directory:
     cd /workspace/smart-parking-lot-v2/src && uv run python manage.py test parking.tests.test_api_vehicles
     cd /workspace/smart-parking-lot-v2/src && uv run python manage.py test
5. If a test fails because of a genuine application bug (not a test bug), do NOT change application code — stop and report the bug.

Report back: the exact file created, the list of test method names, the number of tests in the module, and the full pass/fail summary of both test runs.

Validation (run in subagent): new module src/parking/tests/test_api_vehicles.py with 5 tests (create 201 with/without customer, duplicate registration 400, invalid type or unknown customer 400, list+retrieve). parking.tests.test_api_vehicles -> Ran 5 tests OK; full suite -> Ran 155 tests OK. No existing test files or application code modified.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added dedicated API test module src/parking/tests/test_api_vehicles.py covering /api/vehicles/ via the DRF test client (5 tests, within the cap): create with/without customer, duplicate registration 400, invalid vehicle_type/unknown customer 400, list+retrieve. Verified by running the module (5/5 pass) and the full suite (155/155 pass) in a subagent.
<!-- SECTION:FINAL_SUMMARY:END -->
