---
id: TASK-3.3
title: Implement Early Bird and Night Owl policies
status: To Do
assignee: []
created_date: '2026-09-28 16:03'
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
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The special flat-rate policies share time-window validation and loyalty discount behavior, but each has distinct same-day or next-day applicability rules. Both must be invalidated for stays longer than 24 hours.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Early Bird applies only to same-calendar-day stays with entry from 06:00 inclusive to 09:00 exclusive and exit from 15:30 inclusive to 19:00 exclusive.
- [ ] #2 Night Owl applies only when entry is from 18:00 inclusive through the end of day and exit is from 05:00 inclusive to 10:00 exclusive on the next consecutive calendar day.
- [ ] #3 Both policies are marked not applicable for stays longer than 24 hours.
- [ ] #4 Both policies apply loyalty discounts for SILVER, GOLD, and PLATINUM and no discount for NONE.
- [ ] #5 Both policies include audit details for base amount, loyalty tier, discount, vehicle multiplier, applicability reason, and final amount.
<!-- AC:END -->
