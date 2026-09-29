---
id: TASK-7.3
title: Add API tests for the spots endpoint
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
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Cover /api/spots/ (ParkingSpotViewSet, full CRUD). The endpoint manages parking spots identified by level and number with a spot type. Tests should hit the real HTTP layer via the DRF test client. Keep the module to at most 5 tests focused on the most important behaviors.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Creating a spot with a valid level, number, and spot type returns 201 and the created representation
- [ ] #2 Listing and retrieving spots returns the persisted records
- [ ] #3 A duplicate level and number pair is rejected with 400
- [ ] #4 Invalid spot type or missing fields are rejected with 400
- [ ] #5 The module contains no more than 5 tests
<!-- AC:END -->
