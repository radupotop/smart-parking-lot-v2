---
id: TASK-8
title: Return 400 when deleting a spot referenced by a session
status: Done
assignee:
  - '@qwen'
created_date: '2026-09-29 12:49'
updated_date: '2026-09-29 12:53'
labels:
  - backend
  - api
  - bug
dependencies: []
priority: high
type: bug
ordinal: 29000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
ParkingSession.spot is on_delete=PROTECT, but ParkingSpotViewSet is a plain ModelViewSet with no ProtectedError handling. DELETE /api/spots/{id}/ on an in-use spot therefore raises ProtectedError and the client receives a 500 instead of a clean client error. This was exposed by test_delete_spot_referenced_by_session_is_rejected in src/parking/tests/test_api_spots.py (added under TASK-7.3), which pins the intended 400 behavior and currently fails.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 DELETE /api/spots/{id}/ for a spot referenced by any ParkingSession returns 400 with an error body
- [x] #2 The spot is not deleted when the request is rejected
- [x] #3 DELETE /api/spots/{id}/ for a spot without sessions still returns 204
- [x] #4 test_delete_spot_referenced_by_session_is_rejected passes unmodified
- [x] #5 The full test suite passes
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. In src/parking/views.py, override destroy() on ParkingSpotViewSet: call self.get_object(), attempt instance.delete() inside try/except django.db.models.deletion.ProtectedError, return Response({'detail': ...}, status=400) on ProtectedError, otherwise Response(status=204).
2. Run the spots API test module and the full suite from src/ with 'uv run python manage.py test'.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Overrode ParkingSpotViewSet.destroy to catch ProtectedError and return 400 with a detail message; 204 on success. Verified: spots module 8/8 OK, full suite 163/163 OK. Test file untouched.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
ParkingSpotViewSet.destroy now catches ProtectedError from the PROTECT ParkingSession.spot FK and returns 400 with a readable detail instead of 500, keeping the spot. Verified with 'uv run python manage.py test' from src/: test_delete_spot_referenced_by_session_is_rejected passes unmodified, spots module 8/8 OK, full suite 163/163 OK.
<!-- SECTION:FINAL_SUMMARY:END -->
