---
id: TASK-3.1
title: Add shared pricing constants and helpers
status: To Do
assignee: []
created_date: '2026-09-28 16:02'
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
- [ ] #1 Vehicle multipliers are available for MOTORCYCLE, CAR, and BUS.
- [ ] #2 Loyalty discounts are available for NONE, SILVER, GOLD, and PLATINUM.
- [ ] #3 Standard hourly base rates, peak multiplier, Early Bird rate, and Night Owl rate match the PRD.
- [ ] #4 Time-window helpers support inclusive starts and exclusive ends where required by the PRD.
- [ ] #5 Weekday detection excludes configured PublicHoliday dates.
- [ ] #6 Currency calculations use Decimal values and produce two-decimal-place amounts.
<!-- AC:END -->
