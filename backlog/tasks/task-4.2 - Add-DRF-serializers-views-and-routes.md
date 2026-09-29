---
id: TASK-4.2
title: Add DRF serializers views and routes
status: Done
assignee:
  - '@Qwen'
created_date: '2026-09-28 16:03'
updated_date: '2026-09-29 00:36'
labels:
  - backend
  - api
  - drf
dependencies: []
references:
  - specs/PRD1.md
  - specs/SRS2.md
parent_task_id: TASK-4
priority: medium
type: task
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
SRS2 identifies this as a DRF app, while the PRD describes automated entry and exit interactions. The API should expose the parking session workflow and the persisted audit results without forcing clients to understand internal model details.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Serializers exist for customers, vehicles, parking spots, parking sessions, and rate evaluations needed by the workflow.
- [x] #2 Session read responses include selected policy, charged amount, and per-policy evaluation audit data.
- [x] #3 Views or viewsets support creating/listing/retrieving sessions.
- [x] #4 An exit or calculate action records exit data and returns the final charge.
- [x] #5 API validation errors are clear for missing data, incompatible spot assignments, and invalid session state.
- [x] #6 Project URL configuration exposes the API routes.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add src/parking/serializers.py: serializers for Customer, Vehicle, ParkingSpot, ParkingSession (nested evaluation audit + selected policy + charged amount), RateEvaluation. 2. Add src/parking/views.py: viewsets for customers/vehicles/spots (read + create) and ParkingSessionViewSet with create (entry via record_entry), list, retrieve, and a custom exit action calling record_exit. 3. Map service exceptions to clear DRF error responses (400/409 with readable detail). 4. Wire routes in src/config/urls.py (e.g. /api/... via DRF router). 5. Add API tests (APITestCase) covering all six ACs incl. validation errors. 6. Verify with: cd src && uv run python manage.py check && uv run python manage.py test.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Finalization verification (2026-09-28): 'uv run python manage.py check' -> no issues. 'uv run python manage.py test' -> Ran 83 tests, OK. AC evidence from parking.test_api (21 tests, all ok): AC1 CustomerApiTests/ParkingSpotApiTests/VehicleApiTests create+list tests; AC2 test_list_and_retrieve_include_audit_data_after_exit, test_retrieve_open_session_before_exit; AC3 test_entry_creates_open_session, list/retrieve tests; AC4 test_exit_records_exit_data_and_returns_final_charge; AC5 test_entry_rejects_missing_data, test_entry_rejects_incompatible_spot, test_exit_rejects_invalid_exited_at, test_exit_returns_422_when_no_policy_applies, test_exit_rejects_missing_session; AC6 all tests exercise /api/ routes via DefaultRouter in config/urls.py.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added DRF layer for the ticket workflow: parking/serializers.py (customer, vehicle, spot, rate evaluation, session create/exit/read serializers with nested audit data and read-only billing fields), parking/views.py (ModelViewSets for customers/vehicles/spots; SessionViewSet delegating create to record_entry and a POST exit action to record_exit; sessions are GET/POST only), and DefaultRouter routes under /api/ in config/urls.py. Service exceptions map to 400 (validation, incompatible spot, invalid session state), 422 (no applicable rate policy), 404 (missing session); repeated exit is an idempotent 200. Verified with 21 new APITestCase tests in parking/test_api.py; full suite 83 tests OK and manage.py check clean via direct 'uv run python manage.py' (no Podman).
<!-- SECTION:FINAL_SUMMARY:END -->
