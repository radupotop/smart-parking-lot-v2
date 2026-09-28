---
id: TASK-4.2
title: Add DRF serializers views and routes
status: To Do
assignee: []
created_date: '2026-09-28 16:03'
labels:
  - backend
  - api
  - drf
dependencies: []
references:
  - specs/PRD1.md
  - specs/SRS2.md
parent_task_id: TASK-4
priority: medium
type: task
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
SRS2 identifies this as a DRF app, while the PRD describes automated entry and exit interactions. The API should expose the parking session workflow and the persisted audit results without forcing clients to understand internal model details.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Serializers exist for customers, vehicles, parking spots, parking sessions, and rate evaluations needed by the workflow.
- [ ] #2 Session read responses include selected policy, charged amount, and per-policy evaluation audit data.
- [ ] #3 Views or viewsets support creating/listing/retrieving sessions.
- [ ] #4 An exit or calculate action records exit data and returns the final charge.
- [ ] #5 API validation errors are clear for missing data, incompatible spot assignments, and invalid session state.
- [ ] #6 Project URL configuration exposes the API routes.
<!-- AC:END -->
