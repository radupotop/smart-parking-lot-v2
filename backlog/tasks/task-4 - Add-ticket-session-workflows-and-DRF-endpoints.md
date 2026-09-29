---
id: TASK-4
title: Add ticket session workflows and DRF endpoints
status: Done
assignee:
  - '@Qwen'
created_date: '2026-09-28 15:51'
updated_date: '2026-09-29 00:43'
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
- [x] #1 A session entry workflow can create an open ParkingSession with vehicle, spot, customer context, and entered_at timestamp.
- [x] #2 A session exit workflow can set exited_at, run the rate calculator, persist all RateEvaluations, selected evaluation, and charged amount.
- [x] #3 Workflow validation rejects incompatible vehicle and spot type combinations.
- [x] #4 Workflow validation prevents calculating a final charge for sessions without required entry, vehicle, spot, or exit data.
- [x] #5 DRF serializers expose session, vehicle, spot, customer, charge, selected policy, and evaluation audit data needed by clients.
- [x] #6 DRF views or viewsets provide basic create, retrieve, list, and exit/calculate operations for parking sessions.
- [x] #7 The Django admin can inspect sessions, selected evaluations, and the per-policy evaluation audit trail.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Finalization verification (2026-09-28): 'uv run python manage.py check' -> no issues. 'uv run python manage.py test' -> Ran 86 tests, OK. AC1-AC4 verified by TASK-4.1 evidence (parking.test_services, 16 tests); AC5-AC6 verified by TASK-4.2 evidence (parking.test_api, 21 tests); AC7 verified by new parking/test_admin.py (3 tests, all ok): session changelist renders, session change page shows charged amount + selected evaluation + per-policy audit inline (Standard/Early Bird/Night Owl), rate evaluation changelist renders.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Delivered the automated ticket billing workflow end to end: entry/exit application services (TASK-4.1, parking/services.py) and the DRF API layer (TASK-4.2, parking/serializers.py, parking/views.py, /api/ routes) so sessions can be created, listed, retrieved, and exited with the rate calculator persisting all evaluations, the selected evaluation, and the charged amount. Incompatible vehicle/spot combinations and invalid session states return clear 400/422 errors; repeated exit is an idempotent no-op. Django admin exposes session inspection with a read-only per-policy evaluation audit inline. Verified with 40 dedicated tests across parking/test_services.py, parking/test_api.py, and parking/test_admin.py; full suite 86 tests OK and manage.py check clean via direct 'uv run python manage.py' (no Podman).
<!-- SECTION:FINAL_SUMMARY:END -->
