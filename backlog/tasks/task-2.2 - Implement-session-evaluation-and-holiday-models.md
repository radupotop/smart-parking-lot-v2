---
id: TASK-2.2
title: Implement session evaluation and holiday models
status: Done
assignee:
  - '@codex'
created_date: '2026-09-28 16:02'
updated_date: '2026-09-28 20:51'
labels:
  - backend
  - django
  - models
dependencies: []
references:
  - specs/PRD1.md
  - specs/SRS1.md
  - specs/ERD1.md
parent_task_id: TASK-2
priority: high
type: task
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The ticket is the central transaction record, and RateEvaluation is the audit bridge between Python pricing policies and persisted billing results. Public holidays are needed because weekday peak pricing excludes them.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 ParkingSession stores vehicle, spot, optional customer, entered_at, optional exited_at, status, loyalty tier snapshot, charged amount, and selected evaluation.
- [x] #2 ParkingSession preserves historical billing context instead of relying only on the current vehicle-to-customer relationship.
- [x] #3 RateEvaluation stores session, policy, applicable flag, nullable amount, JSON details, and created_at.
- [x] #4 PublicHoliday stores a unique date and display name.
- [x] #5 Migrations create all session, evaluation, and holiday tables with the required constraints.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add SessionStatus and RatePolicy TextChoices plus ParkingSession, RateEvaluation, and PublicHoliday models matching SRS/ERD fields and relationships. 2. Generate a Django migration after 0001_initial for the new tables and constraints. 3. Add focused ORM tests for defaults, historical customer/loyalty snapshots, evaluation audit JSON, selected evaluation linkage, holiday uniqueness, and readable strings. 4. Rebuild and verify through the Podman Compose test service only.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented ParkingSession, RateEvaluation, and PublicHoliday models with session/rate policy choices, historical customer and loyalty snapshot fields, selected evaluation linkage, and migration 0002. Verified only in containers after rebuilding the compose test image: podman compose --profile tools run --rm test uv run python manage.py makemigrations --check --dry-run; podman compose --profile tools run --rm test uv run python manage.py check; podman compose --profile tools run --rm test (13 tests).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added the session transaction, rate-evaluation audit, and public-holiday persistence layer with focused ORM tests. Container verification passed after rebuilding the test image: migration dry-run had no changes, Django check had no issues, and the compose test service ran 13 tests successfully.
<!-- SECTION:FINAL_SUMMARY:END -->
