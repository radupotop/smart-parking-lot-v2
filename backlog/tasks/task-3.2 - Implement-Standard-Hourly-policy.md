---
id: TASK-3.2
title: Implement Standard Hourly policy
status: Done
assignee:
  - '@codex'
created_date: '2026-09-28 16:03'
updated_date: '2026-09-28 22:18'
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
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Standard Hourly is the fallback policy and the only valid policy for stays over 24 hours. It has the most detailed per-hour behavior because each rounded floating block must be checked for weekday peak overlap.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The policy is applicable to completed sessions with valid entry and exit timestamps.
- [x] #2 Duration is rounded upward to the nearest full hour.
- [x] #3 Hourly blocks start at the exact entry timestamp rather than fixed clock-hour boundaries.
- [x] #4 The first hour uses the initial rate, the second hour uses the second-hour rate, and all later hours use the subsequent-hour rate.
- [x] #5 Any block with partial overlap against a weekday peak window receives the full peak multiplier for that block.
- [x] #6 Peak windows use inclusive starts and exclusive ends.
- [x] #7 The policy returns audit details for every hourly block, including start, end, base rate, peak flag, multiplier, and amount.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add a Standard Hourly policy result type and policy class in src/parking/pricing.py that returns JSON-friendly audit data without persistence. 2. Implement applicability checks, rounded floating hourly blocks, base-rate progression, vehicle multiplier, and weekday/non-holiday peak detection per block. 3. Add focused tests for applicability, invalid/open sessions, rounding, floating block boundaries, base rates, peak edge cases, holidays, and vehicle multipliers. 4. Rebuild and verify only through the Podman Compose test service.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented StandardHourlyPolicy with PolicyResult output, rounded floating hourly blocks, per-block base/peak/vehicle multipliers, JSON-friendly audit details, and inapplicable reasons for missing/invalid timestamps. Container verification passed after rebuilding: podman compose build test; podman compose --profile tools run --rm test uv run python manage.py makemigrations --check --dry-run; podman compose --profile tools run --rm test uv run python manage.py check; podman compose --profile tools run --rm test (34 tests).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added Standard Hourly policy evaluation with Decimal amounts, rounded entry-based hourly blocks, weekday/non-holiday peak surcharge detection, vehicle multipliers, and per-block JSON-friendly audit details. Verified inside Podman Compose containers with rebuild, migration dry-run, Django check, and full test suite (34 tests).
<!-- SECTION:FINAL_SUMMARY:END -->
