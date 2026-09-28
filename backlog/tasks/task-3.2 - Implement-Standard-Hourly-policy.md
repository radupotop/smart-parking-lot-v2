---
id: TASK-3.2
title: Implement Standard Hourly policy
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
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Standard Hourly is the fallback policy and the only valid policy for stays over 24 hours. It has the most detailed per-hour behavior because each rounded floating block must be checked for weekday peak overlap.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The policy is applicable to completed sessions with valid entry and exit timestamps.
- [ ] #2 Duration is rounded upward to the nearest full hour.
- [ ] #3 Hourly blocks start at the exact entry timestamp rather than fixed clock-hour boundaries.
- [ ] #4 The first hour uses the initial rate, the second hour uses the second-hour rate, and all later hours use the subsequent-hour rate.
- [ ] #5 Any block with partial overlap against a weekday peak window receives the full peak multiplier for that block.
- [ ] #6 Peak windows use inclusive starts and exclusive ends.
- [ ] #7 The policy returns audit details for every hourly block, including start, end, base rate, peak flag, multiplier, and amount.
<!-- AC:END -->
