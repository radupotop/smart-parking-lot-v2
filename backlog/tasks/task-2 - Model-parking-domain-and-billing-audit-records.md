---
id: TASK-2
title: Model parking domain and billing audit records
status: Done
assignee:
  - '@codex'
created_date: '2026-09-28 15:51'
updated_date: '2026-09-28 20:58'
labels:
  - backend
  - django
  - models
dependencies:
  - TASK-1
references:
  - specs/PRD1.md
  - specs/SRS1.md
  - specs/ERD1.md
priority: high
type: feature
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The PRD and SRS define the ticket as the persisted parking session and recommend relational storage for domain facts, inputs, compatibility, holidays, and pricing audit output. Pricing behavior should remain in Python policy classes rather than becoming a database rules engine.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Models exist for Customers, Vehicles, ParkingSpots, SpotTypeVehicleCompatibilities, ParkingSessions, RateEvaluations, and PublicHolidays.
- [x] #2 Vehicle type, spot type, loyalty tier, session status, and rate policy values are constrained to the domain values from the specs.
- [x] #3 Parking spot level and number are unique together, and spot type to vehicle type compatibility is unique per pair.
- [x] #4 ParkingSessions store entered_at, optional exited_at, vehicle, spot, optional customer, loyalty tier snapshot, charged amount, and selected evaluation.
- [x] #5 RateEvaluations store policy, applicability, nullable amount, JSON calculation details, and their ParkingSession relationship.
- [x] #6 PublicHolidays enforce one row per calendar date.
- [x] #7 Relevant models are registered in the Django admin with useful list displays and filters.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Implement foundational customer, vehicle, spot, and compatibility models. 2. Add session, rate-evaluation, and public-holiday audit models. 3. Register all parking domain and audit records in Django admin. 4. Verify the completed model/admin layer inside Podman Compose containers.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Completed via TASK-2.1, TASK-2.2, and TASK-2.3. The final model set includes customer, vehicle, spot, compatibility, session/ticket, rate-evaluation audit, and public-holiday records with constrained choices and required uniqueness constraints.

Final verification ran inside Podman Compose containers after rebuilding the image: makemigrations --check --dry-run reported no changes, Django check reported no issues, and the compose test service passed 17 tests.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Completed the parking domain and billing audit persistence layer plus admin registration. Verified inside Podman Compose containers with migration drift check, Django system check, and the full 17-test suite.
<!-- SECTION:FINAL_SUMMARY:END -->
