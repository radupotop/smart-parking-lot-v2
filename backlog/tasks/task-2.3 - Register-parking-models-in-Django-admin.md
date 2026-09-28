---
id: TASK-2.3
title: Register parking models in Django admin
status: Done
assignee:
  - '@codex'
created_date: '2026-09-28 16:02'
updated_date: '2026-09-28 20:56'
labels:
  - backend
  - django
  - admin
dependencies: []
references:
  - specs/SRS1.md
  - specs/SRS2.md
modified_files:
  - src/parking/admin.py
  - src/parking/tests.py
parent_task_id: TASK-2
priority: medium
type: task
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
SRS2 asks for a basic admin panel, and SRS1 emphasizes that RateEvaluation exists for audit and debugging. The admin should make the domain records and billing audit trail easy to inspect during development.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Customers, Vehicles, ParkingSpots, SpotTypeVehicleCompatibilities, ParkingSessions, RateEvaluations, and PublicHolidays are registered in admin.
- [x] #2 Admin list displays include the fields most useful for identifying records without opening each row.
- [x] #3 Admin filters or search fields support common lookups for vehicle registration, session status, policy, date, and loyalty tier.
- [x] #4 ParkingSession admin makes selected evaluation and related policy evaluations inspectable.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Register every parking domain/audit model with focused ModelAdmin classes.
2. Add a read-only RateEvaluation inline to ParkingSession admin and keep RateEvaluation directly registered for audit inspection.
3. Add tests against admin.site registry and ModelAdmin configuration for list displays, filters, searches, and selected/related evaluation visibility.
4. Rebuild the compose test image and run migrations, system checks, and tests inside Podman.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented Django admin registrations for all parking domain and audit models. ParkingSession now shows selected_evaluation and includes a read-only RateEvaluation inline with change links; RateEvaluation is also directly registered for audit inspection. Added admin registry/configuration tests for registrations, list displays, filters/search fields, and evaluation visibility.

Container verification passed after `podman compose build test`: `podman compose --profile tools run --rm test uv run python manage.py makemigrations --check --dry-run` (no changes detected), `podman compose --profile tools run --rm test uv run python manage.py check` (0 issues), and `podman compose --profile tools run --rm test` (17 tests passed).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Registered Customer, Vehicle, ParkingSpot, SpotTypeVehicleCompatibility, ParkingSession, RateEvaluation, and PublicHoliday in Django admin with useful list displays, filters/searches, and read-only audit visibility for session evaluations. Verified inside Podman Compose containers with migration drift check, Django system check, and the full 17-test suite.
<!-- SECTION:FINAL_SUMMARY:END -->
