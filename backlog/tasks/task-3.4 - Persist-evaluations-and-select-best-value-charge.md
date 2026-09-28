---
id: TASK-3.4
title: Persist evaluations and select best-value charge
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
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The PRD mandates exhaustive policy evaluation and lowest valid fare selection. SRS1 recommends RateEvaluation as the audit record for each policy run, with ParkingSession pointing at the selected result.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The calculator runs all configured policies for a completed session.
- [ ] #2 The calculator creates or refreshes RateEvaluation records for every considered policy.
- [ ] #3 Not-applicable policies are persisted with a null amount and explanatory details.
- [ ] #4 The selected evaluation is the applicable policy with the lowest amount.
- [ ] #5 ParkingSession charged amount and selected evaluation are updated atomically with the persisted evaluations.
- [ ] #6 The calculator handles the no-applicable-policy case with a clear domain error.
<!-- AC:END -->
