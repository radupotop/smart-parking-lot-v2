---
id: TASK-7.4
title: Add API tests for the sessions endpoint
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
ordinal: 27000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Cover /api/sessions/ (SessionViewSet: create, list, retrieve). Sessions are lifecycle-managed by the entry service, so the endpoint-specific rules are: entry validates vehicle/spot compatibility, defaults customer to the vehicle owner, and PUT/PATCH/DELETE are not allowed. Tests should hit the real HTTP layer via the DRF test client. Keep the module to at most 5 tests focused on the most important behaviors.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Creating a session (ticket entry) with a compatible vehicle and spot returns 201 with an open session
- [ ] #2 Entry with an incompatible vehicle and spot type is rejected with 400
- [ ] #3 Entry with an unknown vehicle, spot, or invalid entered_at is rejected with 400
- [ ] #4 Listing and retrieving sessions returns the persisted records
- [ ] #5 Update and delete requests on a session are not allowed (405)
- [ ] #6 The module contains no more than 5 tests
<!-- AC:END -->
