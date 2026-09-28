---
id: TASK-4.1
title: Implement ticket entry and exit services
status: To Do
assignee: []
created_date: '2026-09-28 16:03'
labels:
  - backend
  - workflow
  - billing
dependencies: []
references:
  - specs/PRD1.md
  - specs/SRS1.md
parent_task_id: TASK-4
priority: high
type: task
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The product flow starts when a ticket is issued at entry and finishes when the driver exits and the engine calculates the fee. These application services should keep that workflow reusable from admin, API, and tests.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Entry service creates an open ParkingSession with vehicle, spot, customer context, loyalty tier snapshot, and entered_at timestamp.
- [ ] #2 Entry service validates vehicle and spot compatibility.
- [ ] #3 Exit service records exited_at, validates the session can be closed, and calls the rate calculator.
- [ ] #4 Exit service persists evaluations, selected evaluation, charged amount, and closed status.
- [ ] #5 Repeated exit calculation is either prevented or handled idempotently with documented behavior.
<!-- AC:END -->
