---
id: TASK-2.2
title: Implement session evaluation and holiday models
status: To Do
assignee: []
created_date: '2026-09-28 16:02'
labels:
  - backend
  - django
  - models
dependencies: []
references:
  - specs/PRD1.md
  - specs/SRS1.md
  - specs/ERD1.md
parent_task_id: TASK-2
priority: high
type: task
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The ticket is the central transaction record, and RateEvaluation is the audit bridge between Python pricing policies and persisted billing results. Public holidays are needed because weekday peak pricing excludes them.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 ParkingSession stores vehicle, spot, optional customer, entered_at, optional exited_at, status, loyalty tier snapshot, charged amount, and selected evaluation.
- [ ] #2 ParkingSession preserves historical billing context instead of relying only on the current vehicle-to-customer relationship.
- [ ] #3 RateEvaluation stores session, policy, applicable flag, nullable amount, JSON details, and created_at.
- [ ] #4 PublicHoliday stores a unique date and display name.
- [ ] #5 Migrations create all session, evaluation, and holiday tables with the required constraints.
<!-- AC:END -->
