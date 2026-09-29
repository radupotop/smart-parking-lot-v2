---
id: TASK-7.1
title: Add API tests for the customers endpoint
status: Done
assignee:
  - '@Qwen'
created_date: '2026-09-29 11:09'
updated_date: '2026-09-29 11:24'
labels:
  - backend
  - api
  - tests
dependencies: []
parent_task_id: TASK-7
priority: medium
type: task
ordinal: 24000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Cover /api/customers/ (CustomerViewSet, full CRUD). The endpoint exposes loyalty tier management; tests should hit the real HTTP layer via the DRF test client. Keep the module to at most 5 tests focused on the most important behaviors.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Creating a customer with a valid loyalty tier returns 201 and the created representation
- [x] #2 Listing and retrieving customers returns the persisted records
- [x] #3 Updating and deleting a customer work as expected
- [x] #4 Invalid loyalty tier input is rejected with 400
- [x] #5 The module contains no more than 5 tests
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create a new dedicated test module src/parking/tests/test_api_customers.py (do not modify existing test files) with at most 5 tests for /api/customers/ covering: create 201, list/retrieve, update/delete, invalid loyalty tier 400. 2. Run the new module and the full suite via uv run python manage.py test. 3. Verify each acceptance criterion against the test results.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
You are implementing backlog task TASK-7.1: "Add API tests for the customers endpoint" for the Django REST Framework project in /workspace/smart-parking-lot-v2 (Python project root: /workspace/smart-parking-lot-v2/src).

Goal: add a NEW dedicated API test module for the /api/customers/ endpoint (CustomerViewSet, full CRUD). Do NOT modify or reuse any existing test file — create a brand new file:

  src/parking/tests/test_api_customers.py

Requirements:
1. First read for conventions (do not modify them):
   - src/parking/tests/test_api.py  (existing API test style/fixtures)
   - src/parking/views.py, src/parking/serializers.py, src/parking/models.py
2. Write at most 5 tests in the new module, hitting the real HTTP layer with the DRF test client (rest_framework.test.APIClient), covering:
   - Creating a customer with a valid loyalty tier (e.g. "gold") returns 201 and the created representation (id, loyalty_tier, created_at, updated_at).
   - Listing and retrieving customers returns the persisted records.
   - Updating (PATCH or PUT) and deleting a customer work as expected.
   - Invalid loyalty tier input (e.g. "diamond") is rejected with 400.
   You may combine list+retrieve or update+delete within one test to stay within the 5-test cap.
3. Follow the existing test conventions (Django TestCase, helper factories if present in test_api.py, naming style).
4. Run the new module, then the full suite, from the src/ directory:
     cd /workspace/smart-parking-lot-v2/src && uv run python manage.py test parking.tests.test_api_customers
     cd /workspace/smart-parking-lot-v2/src && uv run python manage.py test
5. If a test fails because of a genuine application bug (not a test bug), do NOT change application code — stop and report the bug.

Report back: the exact file created, the list of test method names, the number of tests in the module, and the full pass/fail summary of both test runs.

Validation (run in subagent): new module src/parking/tests/test_api_customers.py with 5 tests (create 201, invalid tier 400, list+retrieve, update, delete). parking.tests.test_api_customers -> Ran 5 tests OK; full suite -> Ran 150 tests OK. No existing test files or application code modified.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added dedicated API test module src/parking/tests/test_api_customers.py covering /api/customers/ CRUD via the DRF test client (5 tests, within the cap). Verified by running the module (5/5 pass) and the full suite (150/150 pass) in a subagent.
<!-- SECTION:FINAL_SUMMARY:END -->
