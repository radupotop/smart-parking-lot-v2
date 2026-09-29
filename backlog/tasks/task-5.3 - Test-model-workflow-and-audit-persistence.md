---
id: TASK-5.3
title: Test model workflow and audit persistence
status: In Progress
assignee:
  - '@Qwen'
created_date: '2026-09-28 16:03'
updated_date: '2026-09-29 02:27'
labels:
  - backend
  - tests
  - django
dependencies: []
references:
  - specs/SRS1.md
  - specs/SRS2.md
  - specs/ERD1.md
parent_task_id: TASK-5
priority: high
type: task
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The relational model and services need coverage around constraints, session lifecycle, compatibility validation, and the RateEvaluation audit trail. These tests complement the pure pricing scenarios by checking that calculated results are stored correctly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Tests cover model constraints for unique vehicle registration, parking spot identity, compatibility pairs, and public holiday dates.
- [ ] #2 Tests cover entry workflow creating an open session with loyalty tier snapshot.
- [ ] #3 Tests cover incompatible vehicle and spot type rejection.
- [ ] #4 Tests cover exit workflow closing a session and storing charged amount and selected evaluation.
- [ ] #5 Tests cover one RateEvaluation record per considered policy with expected applicability and details.
- [ ] #6 The project test command runs all unit tests successfully.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Audit existing coverage (parking/tests/) for model constraints, session lifecycle, and audit persistence to fill gaps rather than duplicate. 2. Add src/parking/tests/test_model_workflow.py covering all six ACs: unique vehicle registration, spot level+number identity, compatibility pair uniqueness, public holiday date uniqueness; entry workflow open session + loyalty snapshot; incompatible vehicle/spot rejection; exit workflow closed session + charged amount + selected evaluation; one RateEvaluation per considered policy with applicability + details; full suite green. 3. Verify: cd src && uv run python manage.py check && uv run python manage.py test.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Subagent instructions (as-is):

You are implementing Backlog task TASK-5.3 "Test model workflow and audit persistence" in the Django project at /workspace/smart-parking-lot-v2. This is a TEST-ONLY task: add tests, do not change production code (models, pricing, services, views, serializers, admin, urls, settings). If you believe a test reveals a genuine bug, DO NOT fix it — report it in your final report instead.

CONTEXT TO READ FIRST (use the read tool):
- specs/SRS1.md, specs/SRS2.md, specs/ERD1.md (relational model, constraints, session lifecycle, audit trail)
- src/parking/models.py (Vehicle.registration unique; ParkingSpot unique (level, number) constraint; SpotTypeVehicleCompatibility unique (spot_type, vehicle_type) constraint; PublicHoliday.date unique; ParkingSession fields incl. loyalty_tier_snapshot, charged_amount, selected_evaluation, status; RateEvaluation FK to session with policy/applicable/amount/details)
- src/parking/services.py (record_entry, record_exit, IncompatibleSpotError, SessionExitError, idempotent re-exit)
- src/parking/pricing.py (ParkingRateCalculator.calculate persists one RateEvaluation per policy, selects cheapest applicable, sets session.selected_evaluation + charged_amount)
- src/parking/tests/ (existing coverage and conventions — audit which cases are ALREADY covered in tests.py, test_services.py, test_api.py, test_admin.py, test_standard_hourly.py, test_special_rates.py so you fill gaps rather than duplicate; follow the SimpleNamespace / TestCase conventions)

ACCEPTANCE CRITERIA — each needs at least one dedicated, clearly-named test:
1. Model constraints: duplicate Vehicle.registration rejected; duplicate ParkingSpot (level, number) rejected; duplicate SpotTypeVehicleCompatibility (spot_type, vehicle_type) rejected; duplicate PublicHoliday.date rejected. Use assertRaises(IntegrityError) with transaction rollback as needed.
2. Entry workflow creates an open session with the customer's loyalty tier snapshot (including the no-customer -> "none" default and that later customer tier changes do not alter the snapshot).
3. Incompatible vehicle and spot type rejection (both an explicit mismatch row and a missing compatibility row).
4. Exit workflow closes the session and stores charged_amount and selected_evaluation (status closed, exited_at set, selected evaluation is the cheapest applicable one).
5. Exactly one RateEvaluation record per considered policy (3 rows for the default policy set) with the expected applicable flags, amounts, and non-empty details for each policy; re-running exit does NOT duplicate evaluation rows (idempotent no-op).
6. The project test command runs all unit tests successfully (this is proven by your final full-suite run; no dedicated test needed, but the suite must be green).

IMPLEMENTATION REQUIREMENTS:
- Create src/parking/tests/test_model_workflow.py (note the tests now live in the src/parking/tests/ package).
- Use DB-backed Django TestCase tests throughout (these are persistence tests).
- Where a scenario is already fully covered by an existing test module, do not duplicate it — instead ensure the AC is demonstrably covered and say so in your report with the existing test name.
- Do NOT modify anything under backlog/, do NOT use Podman/Docker, do NOT modify production code, do NOT commit.

TESTING (mandatory):
  cd /workspace/smart-parking-lot-v2/src && uv run python manage.py check
  cd /workspace/smart-parking-lot-v2/src && uv run python manage.py test
All tests (existing 142 + your new ones) must pass and check must be clean. Fix and re-run until green.

FINAL REPORT:
Summarize: which ACs were already partially covered before (with existing test names), files created, test count added, any suspected bugs found (do not fix), and the exact final check + test output (test count + OK/FAILED).
<!-- SECTION:NOTES:END -->
