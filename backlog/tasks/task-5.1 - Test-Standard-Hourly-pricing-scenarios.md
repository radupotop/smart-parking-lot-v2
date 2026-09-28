---
id: TASK-5.1
title: Test Standard Hourly pricing scenarios
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
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Standard Hourly has the densest edge-case surface: rounded floating blocks, progressive rates, weekday peak windows, partial overlap, and public holiday exclusion. These tests protect the fallback policy and the example behavior in the PRD.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Tests cover upward rounding to full hours.
- [ ] #2 Tests cover first-hour, second-hour, and subsequent-hour rates.
- [ ] #3 Tests cover floating hourly blocks that start at the entry timestamp.
- [ ] #4 Tests cover partial peak overlap causing the whole block to receive the peak multiplier.
- [ ] #5 Tests cover inclusive peak starts and exclusive peak ends.
- [ ] #6 Tests cover public holidays disabling weekday peak surcharge behavior.
- [ ] #7 Tests cover vehicle multipliers for motorcycle, car, and bus under Standard Hourly.
<!-- AC:END -->
