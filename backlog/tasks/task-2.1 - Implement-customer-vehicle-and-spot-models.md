---
id: TASK-2.1
title: Implement customer vehicle and spot models
status: To Do
assignee: []
created_date: '2026-09-28 16:02'
labels:
  - backend
  - django
  - models
dependencies: []
references:
  - specs/SRS1.md
  - specs/ERD1.md
parent_task_id: TASK-2
priority: high
type: task
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The SRS splits the relational parking domain into customers, vehicles, spot types, parking spots, and vehicle-to-spot compatibility. These records are the stable inputs used by session workflows and pricing.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Customer stores the current loyalty tier using the configured loyalty choices.
- [ ] #2 Vehicle stores unique registration, vehicle type, and optional customer ownership.
- [ ] #3 ParkingSpot stores level, number, and spot type with a unique level and number constraint.
- [ ] #4 SpotTypeVehicleCompatibility stores unique spot type and vehicle type pairs.
- [ ] #5 Model string representations make admin and debugging output readable.
<!-- AC:END -->
