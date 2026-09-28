---
id: TASK-2.3
title: Register parking models in Django admin
status: To Do
assignee: []
created_date: '2026-09-28 16:02'
labels:
  - backend
  - django
  - admin
dependencies: []
references:
  - specs/SRS1.md
  - specs/SRS2.md
parent_task_id: TASK-2
priority: medium
type: task
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
SRS2 asks for a basic admin panel, and SRS1 emphasizes that RateEvaluation exists for audit and debugging. The admin should make the domain records and billing audit trail easy to inspect during development.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Customers, Vehicles, ParkingSpots, SpotTypeVehicleCompatibilities, ParkingSessions, RateEvaluations, and PublicHolidays are registered in admin.
- [ ] #2 Admin list displays include the fields most useful for identifying records without opening each row.
- [ ] #3 Admin filters or search fields support common lookups for vehicle registration, session status, policy, date, and loyalty tier.
- [ ] #4 ParkingSession admin makes selected evaluation and related policy evaluations inspectable.
<!-- AC:END -->
