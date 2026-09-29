---
id: TASK-4.1
title: Implement ticket entry and exit services
status: In Progress
assignee:
  - '@Qwen'
created_date: '2026-09-28 16:03'
updated_date: '2026-09-28 23:59'
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
- [ ] #1 Entry service creates an open ParkingSession with vehicle, spot, customer context, loyalty tier snapshot, and entered_at timestamp.
- [ ] #2 Entry service validates vehicle and spot compatibility.
- [ ] #3 Exit service records exited_at, validates the session can be closed, and calls the rate calculator.
- [ ] #4 Exit service persists evaluations, selected evaluation, charged amount, and closed status.
- [ ] #5 Repeated exit calculation is either prevented or handled idempotently with documented behavior.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add src/parking/services.py with entry/exit application services. 2. Entry: validate vehicle-spot compatibility via SpotTypeVehicleCompatibility, create open ParkingSession with entered_at and loyalty tier snapshot from customer. 3. Exit: validate session is open and complete, set exited_at and closed status, invoke ParkingRateCalculator.calculate. 4. Document and enforce idempotent repeated-exit behavior. 5. Add Django tests covering entry, exit, compatibility rejection, and repeated exit. 6. Run full suite with: cd src && uv run python manage.py test.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented via subagent: src/parking/services.py (record_entry, record_exit) + src/parking/test_services.py (16 tests). Repeated exit is an idempotent no-op (documented in docstring, tested). Exceptions: ParkingServiceError, IncompatibleSpotError, SessionExitError. Full suite green: 62 tests OK via 'cd src && uv run python manage.py test' (no Podman). Pending: AC verification and finalization.
<!-- SECTION:NOTES:END -->
