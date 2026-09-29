---
id: TASK-7.2
title: Add API tests for the vehicles endpoint
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
ordinal: 25000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Cover /api/vehicles/ (VehicleViewSet, full CRUD). The endpoint manages registrations, vehicle types, and the optional customer owner. Tests should hit the real HTTP layer via the DRF test client. Keep the module to at most 5 tests focused on the most important behaviors.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Creating a vehicle with a valid type and optional customer returns 201 and the created representation
- [ ] #2 Listing and retrieving vehicles returns the persisted records
- [ ] #3 Duplicate registration is rejected with 400
- [ ] #4 Invalid vehicle type or unknown customer is rejected with 400
- [ ] #5 The module contains no more than 5 tests
<!-- AC:END -->
