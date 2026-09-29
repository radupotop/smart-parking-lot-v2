---
id: TASK-5
title: Add core unit test coverage
status: To Do
assignee:
  - '@Qwen'
created_date: '2026-09-28 15:52'
updated_date: '2026-09-28 23:45'
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
- [ ] #1 Unit tests cover vehicle multipliers for motorcycle, car, and bus charges.
- [ ] #2 Unit tests cover Standard Hourly rounding, first-hour and second-hour rates, subsequent-hour rates, and floating hourly block calculation.
- [ ] #3 Unit tests cover weekday peak surcharge, partial peak overlap, inclusive peak starts, exclusive peak ends, and public holiday exclusion.
- [ ] #4 Unit tests cover Early Bird applicability boundaries and loyalty discounts.
- [ ] #5 Unit tests cover Night Owl applicability boundaries, next-consecutive-day requirement, and loyalty discounts.
- [ ] #6 Unit tests cover the greater-than-24-hour rule invalidating Early Bird and Night Owl.
- [ ] #7 Unit tests cover best-value selection when multiple policies are applicable.
- [ ] #8 Unit tests cover persistence of RateEvaluation details and selected evaluation on the ParkingSession.
<!-- AC:END -->
