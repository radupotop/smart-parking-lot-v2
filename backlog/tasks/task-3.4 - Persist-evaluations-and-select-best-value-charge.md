---
id: TASK-3.4
title: Persist evaluations and select best-value charge
status: Done
assignee:
  - '@codex'
created_date: '2026-09-28 16:03'
updated_date: '2026-09-28 22:35'
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
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The PRD mandates exhaustive policy evaluation and lowest valid fare selection. SRS1 recommends RateEvaluation as the audit record for each policy run, with ParkingSession pointing at the selected result.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The calculator runs all configured policies for a completed session.
- [x] #2 The calculator creates or refreshes RateEvaluation records for every considered policy.
- [x] #3 Not-applicable policies are persisted with a null amount and explanatory details.
- [x] #4 The selected evaluation is the applicable policy with the lowest amount.
- [x] #5 ParkingSession charged amount and selected evaluation are updated atomically with the persisted evaluations.
- [x] #6 The calculator handles the no-applicable-policy case with a clear domain error.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add a ParkingRateCalculator orchestration API around the existing policies.
2. Persist refreshed RateEvaluation rows for every configured policy inside a transaction.
3. Select the lowest applicable persisted evaluation and update ParkingSession in the same transaction.
4. Raise NoApplicableRatePolicyError when all configured policies are not applicable while leaving auditable not-applicable evaluations.
5. Add focused tests for configured policy execution, persistence, best-value selection, refresh behavior, session updates, and the domain error path.
6. Rebuild and verify inside the Podman Compose test service.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented ParkingRateCalculator in src/parking/pricing.py with the default policy order StandardHourlyPolicy, EarlyBirdPolicy, NightOwlPolicy. The calculator evaluates every configured policy, refreshes RateEvaluation rows for the session, persists non-applicable policy details with null amounts, selects the lowest applicable persisted evaluation, and updates ParkingSession charged_amount/selected_evaluation inside transaction.atomic(). Added NoApplicableRatePolicyError for all-rejected policy sets.

Added focused tests in src/parking/tests.py covering default policy persistence and Early Bird best-value selection, injected configured-policy execution, rerun refresh behavior without stale rows, and the no-applicable domain error with persisted rejection details.

Container verification passed after rebuilding: podman compose build test; podman compose --profile tools run --rm test uv run python manage.py makemigrations --check --dry-run; podman compose --profile tools run --rm test uv run python manage.py check; podman compose --profile tools run --rm test (46 tests).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented ParkingRateCalculator orchestration for persisted policy evaluation and best-value selection. It evaluates all configured policies, refreshes RateEvaluation audit rows, stores non-applicable results with null amounts/reasons, updates ParkingSession charged_amount and selected_evaluation in an atomic transaction, and raises NoApplicableRatePolicyError when nothing applies. Verified inside Podman Compose after rebuilding: migration dry-run clean, Django check clean, and 46 tests passed.
<!-- SECTION:FINAL_SUMMARY:END -->
