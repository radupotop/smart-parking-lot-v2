---
id: TASK-3.1
title: Add shared pricing constants and helpers
status: Done
assignee:
  - '@codex'
created_date: '2026-09-28 16:02'
updated_date: '2026-09-28 22:12'
labels:
  - backend
  - billing
  - pricing
dependencies: []
references:
  - specs/PRD1.md
  - specs/SRS1.md
parent_task_id: TASK-3
priority: high
type: task
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The policy classes need shared definitions for vehicle multipliers, loyalty discounts, base rates, peak windows, special-rate windows, weekday and public-holiday checks, and currency rounding. Keeping these common inputs together reduces drift between policies.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Vehicle multipliers are available for MOTORCYCLE, CAR, and BUS.
- [x] #2 Loyalty discounts are available for NONE, SILVER, GOLD, and PLATINUM.
- [x] #3 Standard hourly base rates, peak multiplier, Early Bird rate, and Night Owl rate match the PRD.
- [x] #4 Time-window helpers support inclusive starts and exclusive ends where required by the PRD.
- [x] #5 Weekday detection excludes configured PublicHoliday dates.
- [x] #6 Currency calculations use Decimal values and produce two-decimal-place amounts.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add a focused parking.pricing module that exposes Decimal pricing constants keyed by existing model TextChoices. 2. Add reusable currency rounding, time-window containment/overlap, and weekday/public-holiday helpers. 3. Cover constants and helpers with deterministic tests, then verify inside the Podman compose test container.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented src/parking/pricing.py with Decimal vehicle multipliers, loyalty discounts, rate constants, TimeWindow helpers, interval overlap, date-window construction, currency quantization, and weekday/public-holiday detection. Added focused tests in src/parking/tests.py. Container verification passed after rebuilding: podman compose build test; podman compose --profile tools run --rm test uv run python manage.py makemigrations --check --dry-run; podman compose --profile tools run --rm test uv run python manage.py check; podman compose --profile tools run --rm test (25 tests).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added shared pricing constants and reusable helper functions for vehicle multipliers, loyalty discounts, PRD rates, time-window boundary checks, interval overlap, public-holiday-aware weekday detection, and Decimal currency rounding. Verified entirely inside Podman compose containers after rebuilding; migration dry-run reported no changes, Django check passed, and the test suite ran 25 tests successfully.
<!-- SECTION:FINAL_SUMMARY:END -->
