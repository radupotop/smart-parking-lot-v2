---
id: TASK-2.1
title: Implement customer vehicle and spot models
status: Done
assignee:
  - '@codex'
created_date: '2026-09-28 16:02'
updated_date: '2026-09-28 20:39'
labels:
  - backend
  - django
  - models
dependencies: []
references:
  - specs/SRS1.md
  - specs/ERD1.md
parent_task_id: TASK-2
priority: high
type: task
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The SRS splits the relational parking domain into customers, vehicles, spot types, parking spots, and vehicle-to-spot compatibility. These records are the stable inputs used by session workflows and pricing.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Customer stores the current loyalty tier using the configured loyalty choices.
- [x] #2 Vehicle stores unique registration, vehicle type, and optional customer ownership.
- [x] #3 ParkingSpot stores level, number, and spot type with a unique level and number constraint.
- [x] #4 SpotTypeVehicleCompatibility stores unique spot type and vehicle type pairs.
- [x] #5 Model string representations make admin and debugging output readable.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Confirm model requirements from SRS/ERD and current app conventions.
2. Add TextChoices and foundational models with constraints and readable string output.
3. Generate the initial parking migration for these tables.
4. Add focused Django tests covering defaults, choices, optional owner, uniqueness, and string representations.
5. Verify with makemigrations dry-run, Django check, and full test suite before finalizing TASK-2.1.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented Customer, Vehicle, ParkingSpot, and SpotTypeVehicleCompatibility with TextChoices, uniqueness constraints, timestamps where specified by ERD, initial migration, and focused ORM tests. Verified with UV_CACHE_DIR=/tmp/uv-cache uv run python manage.py makemigrations --check --dry-run, check, and test from src/.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented foundational parking domain models, generated the initial migration, and added focused model tests. Verification passed: makemigrations --check --dry-run reported no changes, Django system check reported no issues, and uv run python manage.py test passed 7 tests.
<!-- SECTION:FINAL_SUMMARY:END -->
