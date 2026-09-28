---
id: TASK-4
title: Add ticket session workflows and DRF endpoints
status: To Do
assignee: []
created_date: '2026-09-28 15:51'
labels:
  - backend
  - api
  - workflow
dependencies:
  - TASK-3
references:
  - specs/PRD1.md
  - specs/SRS1.md
  - specs/SRS2.md
priority: medium
type: feature
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The product flow is automated ticket billing: a ticket is issued at entry, and at exit the system calculates and stores the final fee. This task turns the persisted ParkingSession and calculator into usable Django and DRF workflows while keeping API test expansion available for later work.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A session entry workflow can create an open ParkingSession with vehicle, spot, customer context, and entered_at timestamp.
- [ ] #2 A session exit workflow can set exited_at, run the rate calculator, persist all RateEvaluations, selected evaluation, and charged amount.
- [ ] #3 Workflow validation rejects incompatible vehicle and spot type combinations.
- [ ] #4 Workflow validation prevents calculating a final charge for sessions without required entry, vehicle, spot, or exit data.
- [ ] #5 DRF serializers expose session, vehicle, spot, customer, charge, selected policy, and evaluation audit data needed by clients.
- [ ] #6 DRF views or viewsets provide basic create, retrieve, list, and exit/calculate operations for parking sessions.
- [ ] #7 The Django admin can inspect sessions, selected evaluations, and the per-policy evaluation audit trail.
<!-- AC:END -->
