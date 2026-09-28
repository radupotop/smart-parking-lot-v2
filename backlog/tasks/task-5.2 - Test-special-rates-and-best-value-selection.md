---
id: TASK-5.2
title: Test special rates and best-value selection
status: To Do
assignee: []
created_date: '2026-09-28 16:03'
labels:
  - backend
  - tests
  - billing
dependencies: []
references:
  - specs/PRD1.md
  - specs/SRS1.md
parent_task_id: TASK-5
priority: high
type: task
ordinal: 19000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Early Bird and Night Owl depend on precise time-window boundaries, loyalty discounts, vehicle multipliers, and the rule that specials are invalid for stays over 24 hours. Best-value tests confirm the engine honors the core product promise of charging the cheapest valid fare.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Tests cover Early Bird entry and exit window boundaries.
- [ ] #2 Tests cover Night Owl entry window, next-consecutive-day exit window, and invalid non-consecutive exits.
- [ ] #3 Tests cover SILVER, GOLD, PLATINUM, and NONE loyalty outcomes for specials.
- [ ] #4 Tests cover vehicle multipliers for motorcycle, car, and bus under flat-rate specials.
- [ ] #5 Tests cover stays longer than 24 hours invalidating Early Bird and Night Owl.
- [ ] #6 Tests cover cases where Standard Hourly and a special both apply and the lowest amount is selected.
<!-- AC:END -->
