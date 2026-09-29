---
id: TASK-7.1
title: Add API tests for the customers endpoint
status: To Do
assignee: []
created_date: '2026-09-29 11:09'
labels:
  - backend
  - api
  - tests
dependencies: []
parent_task_id: TASK-7
priority: medium
type: task
ordinal: 24000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Cover /api/customers/ (CustomerViewSet, full CRUD). The endpoint exposes loyalty tier management; tests should hit the real HTTP layer via the DRF test client. Keep the module to at most 5 tests focused on the most important behaviors.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Creating a customer with a valid loyalty tier returns 201 and the created representation
- [ ] #2 Listing and retrieving customers returns the persisted records
- [ ] #3 Updating and deleting a customer work as expected
- [ ] #4 Invalid loyalty tier input is rejected with 400
- [ ] #5 The module contains no more than 5 tests
<!-- AC:END -->
