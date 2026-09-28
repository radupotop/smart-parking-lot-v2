---
id: TASK-5.3
title: Test model workflow and audit persistence
status: To Do
assignee: []
created_date: '2026-09-28 16:03'
labels:
  - backend
  - tests
  - django
dependencies: []
references:
  - specs/SRS1.md
  - specs/SRS2.md
  - specs/ERD1.md
parent_task_id: TASK-5
priority: high
type: task
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The relational model and services need coverage around constraints, session lifecycle, compatibility validation, and the RateEvaluation audit trail. These tests complement the pure pricing scenarios by checking that calculated results are stored correctly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Tests cover model constraints for unique vehicle registration, parking spot identity, compatibility pairs, and public holiday dates.
- [ ] #2 Tests cover entry workflow creating an open session with loyalty tier snapshot.
- [ ] #3 Tests cover incompatible vehicle and spot type rejection.
- [ ] #4 Tests cover exit workflow closing a session and storing charged amount and selected evaluation.
- [ ] #5 Tests cover one RateEvaluation record per considered policy with expected applicability and details.
- [ ] #6 The project test command runs all unit tests successfully.
<!-- AC:END -->
