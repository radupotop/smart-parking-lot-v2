---
id: TASK-4.1
title: Implement ticket entry and exit services
status: Done
assignee:
  - '@Qwen'
created_date: '2026-09-28 16:03'
updated_date: '2026-09-29 00:12'
labels:
  - backend
  - workflow
  - billing
dependencies: []
references:
  - specs/PRD1.md
  - specs/SRS1.md
parent_task_id: TASK-4
priority: high
type: task
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The product flow starts when a ticket is issued at entry and finishes when the driver exits and the engine calculates the fee. These application services should keep that workflow reusable from admin, API, and tests.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Entry service creates an open ParkingSession with vehicle, spot, customer context, loyalty tier snapshot, and entered_at timestamp.
- [x] #2 Entry service validates vehicle and spot compatibility.
- [x] #3 Exit service records exited_at, validates the session can be closed, and calls the rate calculator.
- [x] #4 Exit service persists evaluations, selected evaluation, charged amount, and closed status.
- [x] #5 Repeated exit calculation is either prevented or handled idempotently with documented behavior.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add src/parking/services.py with entry/exit application services. 2. Entry: validate vehicle-spot compatibility via SpotTypeVehicleCompatibility, create open ParkingSession with entered_at and loyalty tier snapshot from customer. 3. Exit: validate session is open and complete, set exited_at and closed status, invoke ParkingRateCalculator.calculate. 4. Document and enforce idempotent repeated-exit behavior. 5. Add Django tests covering entry, exit, compatibility rejection, and repeated exit. 6. Run full suite with: cd src && uv run python manage.py test.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented via subagent: src/parking/services.py (record_entry, record_exit) + src/parking/test_services.py (16 tests). Repeated exit is an idempotent no-op (documented in docstring, tested). Exceptions: ParkingServiceError, IncompatibleSpotError, SessionExitError. Full suite green: 62 tests OK via 'cd src && uv run python manage.py test' (no Podman). Pending: AC verification and finalization.

Finalization verification (2026-09-28): 'uv run python manage.py check' -> System check identified no issues. 'uv run python manage.py test' -> Ran 62 tests, OK. AC evidence from parking.test_services (16 tests, all ok): AC1 test_entry_defaults_customer_to_vehicle_owner, test_entry_defaults_entered_at_to_now, test_entry_snapshots_customer_loyalty_tier_at_entry_time, test_entry_without_customer_defaults_loyalty_snapshot_to_none; AC2 test_entry_rejects_incompatible_vehicle_and_spot, test_entry_rejects_missing_compatibility_row; AC3 test_exit_defaults_exited_at_to_now, test_exit_rejects_unsaved_session, test_exit_rejects_session_missing_entered_at/vehicle/spot, test_exit_rolls_back_when_no_policy_applies; AC4 test_exit_persists_evaluations_selected_charge_and_closed_status; AC5 test_repeated_exit_is_idempotent_noop.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added parking/services.py with record_entry and record_exit application services for the ticket billing flow. Entry validates vehicle/spot compatibility via SpotTypeVehicleCompatibility and snapshots the customer loyalty tier; exit validates the session, runs ParkingRateCalculator inside a transaction, persists evaluations, selected evaluation, charged amount, and closed status, and rolls back (session stays open) when no policy applies. Repeated exit is an idempotent no-op. New exceptions: ParkingServiceError, IncompatibleSpotError, SessionExitError. Verified with 16 new tests in parking/test_services.py; full suite 62 tests OK and manage.py check clean via direct 'uv run python manage.py' (no Podman).
<!-- SECTION:FINAL_SUMMARY:END -->
