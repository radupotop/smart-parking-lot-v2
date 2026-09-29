---
id: TASK-5.2
title: Test special rates and best-value selection
status: Done
assignee:
  - '@Qwen'
created_date: '2026-09-28 16:03'
updated_date: '2026-09-29 02:19'
labels:
  - backend
  - tests
  - billing
dependencies: []
references:
  - specs/PRD1.md
  - specs/SRS1.md
parent_task_id: TASK-5
priority: high
type: task
ordinal: 19000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Early Bird and Night Owl depend on precise time-window boundaries, loyalty discounts, vehicle multipliers, and the rule that specials are invalid for stays over 24 hours. Best-value tests confirm the engine honors the core product promise of charging the cheapest valid fare.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Tests cover Early Bird entry and exit window boundaries.
- [x] #2 Tests cover Night Owl entry window, next-consecutive-day exit window, and invalid non-consecutive exits.
- [x] #3 Tests cover SILVER, GOLD, PLATINUM, and NONE loyalty outcomes for specials.
- [x] #4 Tests cover vehicle multipliers for motorcycle, car, and bus under flat-rate specials.
- [x] #5 Tests cover stays longer than 24 hours invalidating Early Bird and Night Owl.
- [x] #6 Tests cover cases where Standard Hourly and a special both apply and the lowest amount is selected.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Audit existing special-rate coverage in src/parking/tests.py (EarlyBirdPolicy, NightOwlPolicy, ParkingRateCalculator) to fill gaps rather than duplicate. 2. Add src/parking/test_special_rates.py covering all six ACs: Early Bird entry/exit window boundaries; Night Owl entry window, next-consecutive-day exit, non-consecutive rejection; SILVER/GOLD/PLATINUM/NONE loyalty discounts on flat rates; motorcycle/car/bus multipliers under specials; >24h stays invalidating both specials; best-value selection when Standard and a special both apply (cheapest wins, ties broken by policy order). 3. Use direct policy evaluation for window/loyalty/multiplier cases; DB-backed ParkingRateCalculator tests for best-value selection and persistence. 4. Verify: cd src && uv run python manage.py check && uv run python manage.py test (all green).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Subagent instructions (as-is):

You are implementing Backlog task TASK-5.2 "Test special rates and best-value selection" in the Django project at /workspace/smart-parking-lot-v2. This is a TEST-ONLY task: add tests, do not change production code (models, pricing, services, views). If you believe a test reveals a genuine bug in pricing.py, DO NOT fix it — report it in your final report instead.

CONTEXT TO READ FIRST (use the read tool):
- specs/PRD1.md and specs/SRS1.md (Early Bird, Night Owl, loyalty discount, and best-value rules)
- src/parking/pricing.py (EarlyBirdPolicy: $15.00 flat, entry 06:00-09:00 inclusive start / exclusive end, exit 15:30-19:00, same calendar day; NightOwlPolicy: $8.00 flat, entry 18:00-23:59 inclusive end, exit 05:00-10:00, exit must be next consecutive calendar day; both reject stays > 24h and require a loyalty tier snapshot; LOYALTY_DISCOUNTS none 0 / silver 0.10 / gold 0.20 / platinum 0.30; VEHICLE_MULTIPLIERS motorcycle 0.8 / car 1.0 / bus 2.0; ParkingRateCalculator.calculate: persists all RateEvaluations, selects cheapest applicable, tie-break by policy order (standard, early_bird, night_owl), raises NoApplicableRatePolicyError when none apply)
- src/parking/models.py (ParkingSession, RateEvaluation, LoyaltyTier, VehicleType)
- src/parking/tests.py and src/parking/test_standard_hourly.py (existing coverage and test conventions — audit which special-rate cases are ALREADY covered so you fill gaps rather than duplicate)

ACCEPTANCE CRITERIA — each needs at least one dedicated, clearly-named test:
1. Early Bird entry and exit window boundaries: entry exactly 06:00 (in) / 05:59 (out) / 09:00 (out, exclusive end); exit exactly 15:30 (in) / 19:00 (out, exclusive end); cross-midnight or different-calendar-day stays rejected.
2. Night Owl entry window (entry exactly 18:00 in / 17:59 out / 23:59 in), next-consecutive-day exit window (exit exactly 05:00 in / 10:00 out exclusive), and invalid non-consecutive exits (e.g. exit two days later, or same-day exit) rejected.
3. Loyalty outcomes for specials: NONE (no discount), SILVER (10%), GOLD (20%), PLATINUM (30%) applied to the flat base before the vehicle multiplier, with exact Decimal amounts (e.g. Early Bird car: 15.00 / 13.50 / 12.00 / 10.50).
4. Vehicle multipliers under flat-rate specials: motorcycle 0.8, car 1.0, bus 2.0 (e.g. Night Owl car 8.00, motorcycle 6.40, bus 16.00), including combined loyalty + vehicle math.
5. Stays longer than 24 hours invalidate BOTH Early Bird and Night Owl (boundary: exactly 24h still valid if windows allow, 24h+1s invalid — check the actual code semantics and test what the code does, documenting it).
6. Best-value selection: when Standard Hourly and a special both apply, the cheapest is selected and persisted (session.charged_amount + selected_evaluation); include at least one case where the special wins, one where Standard wins, and document/verify the tie-break by policy order. Use DB-backed ParkingRateCalculator tests for these (real ParkingSession rows) and assert the persisted RateEvaluation audit rows.

IMPLEMENTATION REQUIREMENTS:
- Create src/parking/test_special_rates.py.
- Prefer direct unit tests calling EarlyBirdPolicy().evaluate() / NightOwlPolicy().evaluate() with lightweight session objects (follow the SimpleNamespace convention from test_standard_hourly.py where it works; note special policies read loyalty_tier_snapshot and vehicle.vehicle_type). Use DB-backed TestCase tests for AC6 (calculator + persistence) and anywhere the code touches the ORM.
- Use timezone-aware UTC datetimes consistently; use fixed ISO dates with comments stating the weekday where day-of-week matters.
- Assert exact Decimal amounts and, where useful, the details dict (loyalty_discount, vehicle_multiplier, applicability reasons for rejected cases).
- Do NOT modify anything under backlog/, do NOT use Podman/Docker, do NOT modify production code.

TESTING (mandatory):
  cd /workspace/smart-parking-lot-v2/src && uv run python manage.py check
  cd /workspace/smart-parking-lot-v2/src && uv run python manage.py test
All tests (existing 110 + your new ones) must pass and check must be clean. Fix and re-run until green.

FINAL REPORT:
Summarize: which ACs were already partially covered before, files created, test count added, any suspected pricing bugs found (do not fix), and the final check + test output.

Finalization verification (2026-09-29): 'uv run python manage.py check' -> no issues. 'uv run python manage.py test' -> Ran 142 tests, OK. AC evidence from parking/tests/test_special_rates.py (32 tests, all ok, run in subagent after test-package move): AC1 Early Bird boundary tests (0600/0559/0900 entry, 1530/1900 exit, cross-midnight rejected); AC2 Night Owl entry 1800/2359/1759, exit 0500/1000, same-day and two-days-later rejected; AC3 exact loyalty tier amounts for both specials; AC4 vehicle multipliers + combined loyalty math; AC5 24h+1s invalidates both specials, exactly-24h semantics documented; AC6 DB-backed best-value: special wins, standard wins, exact-tie policy-order tie-breaks with persisted evaluations. Note: all test modules moved to src/parking/tests/ package (git mv, history preserved); no production code changed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added 32 special-rate and best-value tests (now in parking/tests/test_special_rates.py) covering all six acceptance criteria: Early Bird and Night Owl window boundaries with inclusive starts / exclusive ends, loyalty tier exact amounts, vehicle multipliers with combined math, 24h+1s invalidation of both specials, and DB-backed best-value selection with policy-order tie-breaks asserting persisted evaluations. Test-only change; no pricing bugs found. Verified with full suite at 142 tests OK and manage.py check clean via direct 'uv run python manage.py' (no Podman); test run executed in a subagent after relocating all test modules into the src/parking/tests/ package.
<!-- SECTION:FINAL_SUMMARY:END -->
