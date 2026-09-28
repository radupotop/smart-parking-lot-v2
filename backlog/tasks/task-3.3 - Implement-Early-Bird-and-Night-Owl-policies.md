---
id: TASK-3.3
title: Implement Early Bird and Night Owl policies
status: Done
assignee:
  - '@codex'
created_date: '2026-09-28 16:03'
updated_date: '2026-09-28 22:26'
labels:
  - backend
  - billing
  - pricing
dependencies: []
references:
  - specs/PRD1.md
  - specs/SRS1.md
modified_files:
  - src/parking/pricing.py
  - src/parking/tests.py
parent_task_id: TASK-3
priority: high
type: task
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The special flat-rate policies share time-window validation and loyalty discount behavior, but each has distinct same-day or next-day applicability rules. Both must be invalidated for stays longer than 24 hours.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Early Bird applies only to same-calendar-day stays with entry from 06:00 inclusive to 09:00 exclusive and exit from 15:30 inclusive to 19:00 exclusive.
- [x] #2 Night Owl applies only when entry is from 18:00 inclusive through the end of day and exit is from 05:00 inclusive to 10:00 exclusive on the next consecutive calendar day.
- [x] #3 Both policies are marked not applicable for stays longer than 24 hours.
- [x] #4 Both policies apply loyalty discounts for SILVER, GOLD, and PLATINUM and no discount for NONE.
- [x] #5 Both policies include audit details for base amount, loyalty tier, discount, vehicle multiplier, applicability reason, and final amount.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add EarlyBirdPolicy and NightOwlPolicy using shared special-rate validation, discount, vehicle multiplier, and audit-detail helpers.
2. Add focused tests for applicability windows, loyalty tiers, vehicle multipliers, invalid sessions, >24h stays, and detail payloads.
3. Rebuild the compose test image and run all verification inside Podman containers.
4. Finalize TASK-3.3 with evidence-backed AC checks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented EarlyBirdPolicy and NightOwlPolicy as non-persistent PolicyResult evaluators. Added shared special-rate validation for required timestamps, exit-after-entry, >24h invalidation, vehicle type, loyalty snapshot, flat-rate discount math, vehicle multipliers, and JSON-friendly audit details.

Container verification after rebuilding test image:
- podman compose build test
- podman compose --profile tools run --rm test uv run python manage.py makemigrations --check --dry-run -> No changes detected
- podman compose --profile tools run --rm test uv run python manage.py check -> no issues
- podman compose --profile tools run --rm test -> 42 tests passed
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added Early Bird and Night Owl special-rate policy evaluators with shared validation, loyalty discount and vehicle multiplier calculation, and audit detail payloads. Verified all acceptance criteria with focused policy tests plus full containerized checks: migration dry-run clean, Django check clean, and 42 tests passed inside Podman Compose.
<!-- SECTION:FINAL_SUMMARY:END -->
