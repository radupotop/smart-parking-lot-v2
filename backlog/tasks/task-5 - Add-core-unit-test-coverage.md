---
id: TASK-5
title: Add core unit test coverage
status: Done
assignee:
  - '@Qwen'
created_date: '2026-09-28 15:52'
updated_date: '2026-09-29 03:08'
labels:
  - backend
  - tests
  - billing
dependencies:
  - TASK-3
references:
  - specs/PRD1.md
  - specs/SRS1.md
  - specs/SRS2.md
priority: high
type: task
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
SRS2 calls for unit tests now, with API tests to be added later. The highest-risk behavior is the billing calculation and persistence audit trail, so this task captures the core scenarios needed before the implementation can be trusted.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Unit tests cover vehicle multipliers for motorcycle, car, and bus charges.
- [x] #2 Unit tests cover Standard Hourly rounding, first-hour and second-hour rates, subsequent-hour rates, and floating hourly block calculation.
- [x] #3 Unit tests cover weekday peak surcharge, partial peak overlap, inclusive peak starts, exclusive peak ends, and public holiday exclusion.
- [x] #4 Unit tests cover Early Bird applicability boundaries and loyalty discounts.
- [x] #5 Unit tests cover Night Owl applicability boundaries, next-consecutive-day requirement, and loyalty discounts.
- [x] #6 Unit tests cover the greater-than-24-hour rule invalidating Early Bird and Night Owl.
- [x] #7 Unit tests cover best-value selection when multiple policies are applicable.
- [x] #8 Unit tests cover persistence of RateEvaluation details and selected evaluation on the ParkingSession.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Finalization verification (2026-09-29): 'uv run python manage.py check' -> no issues. 'uv run python manage.py test' -> Ran 145 tests, OK (subagent run with stderr progress captured). AC evidence across parking/tests/: AC1 test_standard_hourly.py StandardHourlyVehicleMultiplierTests + test_special_rates.py vehicle multiplier tests; AC2 test_standard_hourly.py Rounding/BaseRate/FloatingBlock test classes; AC3 test_standard_hourly.py PartialPeakOverlap/PeakBoundary/PeakDayRules test classes; AC4 test_special_rates.py Early Bird boundary + loyalty tier tests; AC5 test_special_rates.py Night Owl boundary, next-consecutive-day, and loyalty tests; AC6 test_special_rates.py 24h+1s invalidation tests (both specials); AC7 test_special_rates.py best-value tests (special wins, standard wins, policy-order tie-breaks) + test_model_workflow.py ExitWorkflowSelectionTests; AC8 test_model_workflow.py ExitWorkflowAuditPersistenceTests (per-policy details + selected evaluation persisted) + test_services.py exit persistence test.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Delivered core unit test coverage for the billing engine and persistence audit trail across three subtasks: 24 Standard Hourly scenario tests (rounding, progressive rates, floating blocks, peak overlap/boundaries, holiday exclusion, vehicle multipliers), 32 special-rate and best-value tests (Early Bird/Night Owl windows, loyalty discounts, vehicle multipliers, 24h rule, cheapest-applicable selection with tie-breaks), and 3 model-workflow/audit-persistence tests (exit workflow selection, one RateEvaluation per policy with details, idempotent re-exit). All test modules live in the parking/tests/ package. Verified with the full suite at 145 tests OK and manage.py check clean via direct 'uv run python manage.py' (no Podman); no pricing or persistence bugs found.
<!-- SECTION:FINAL_SUMMARY:END -->
