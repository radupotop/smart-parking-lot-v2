---
id: TASK-2
title: Model parking domain and billing audit records
status: To Do
assignee: []
created_date: '2026-09-28 15:51'
labels:
  - backend
  - django
  - models
dependencies:
  - TASK-1
references:
  - specs/PRD1.md
  - specs/SRS1.md
  - specs/ERD1.md
priority: high
type: feature
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The PRD and SRS define the ticket as the persisted parking session and recommend relational storage for domain facts, inputs, compatibility, holidays, and pricing audit output. Pricing behavior should remain in Python policy classes rather than becoming a database rules engine.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Models exist for Customers, Vehicles, ParkingSpots, SpotTypeVehicleCompatibilities, ParkingSessions, RateEvaluations, and PublicHolidays.
- [ ] #2 Vehicle type, spot type, loyalty tier, session status, and rate policy values are constrained to the domain values from the specs.
- [ ] #3 Parking spot level and number are unique together, and spot type to vehicle type compatibility is unique per pair.
- [ ] #4 ParkingSessions store entered_at, optional exited_at, vehicle, spot, optional customer, loyalty tier snapshot, charged amount, and selected evaluation.
- [ ] #5 RateEvaluations store policy, applicability, nullable amount, JSON calculation details, and their ParkingSession relationship.
- [ ] #6 PublicHolidays enforce one row per calendar date.
- [ ] #7 Relevant models are registered in the Django admin with useful list displays and filters.
<!-- AC:END -->
