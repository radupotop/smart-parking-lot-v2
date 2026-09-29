---
id: TASK-7.5
title: Add API tests for the session exit endpoint
status: To Do
assignee: []
created_date: '2026-09-29 11:10'
labels:
  - backend
  - api
  - tests
dependencies: []
parent_task_id: TASK-7
priority: medium
type: task
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Cover /api/sessions/<id>/exit/ (SessionViewSet.exit action). This is the billing endpoint: it records the exit, runs the rate calculator, and returns the final charge with the per-policy evaluation audit data. Endpoint-specific rules: idempotent on already-closed sessions, 422 when no pricing policy applies, 400 for invalid exit input. Tests should hit the real HTTP layer via the DRF test client. Keep the module to at most 5 tests focused on the most important behaviors.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Exiting an open session returns 200 with the closed session, charged amount, selected evaluation, and per-policy rate evaluations
- [ ] #2 Exiting an already-closed session is idempotent and returns the unchanged session
- [ ] #3 Exiting a session for which no pricing policy applies returns 422 and leaves the session open
- [ ] #4 Invalid exited_at input or a missing session is rejected with 400
- [ ] #5 The module contains no more than 5 tests
<!-- AC:END -->
