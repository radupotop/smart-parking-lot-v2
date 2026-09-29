---
id: TASK-5.1
title: Test Standard Hourly pricing scenarios
status: Done
assignee:
  - '@Qwen'
created_date: '2026-09-28 16:03'
updated_date: '2026-09-29 01:16'
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
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Standard Hourly has the densest edge-case surface: rounded floating blocks, progressive rates, weekday peak windows, partial overlap, and public holiday exclusion. These tests protect the fallback policy and the example behavior in the PRD.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Tests cover upward rounding to full hours.
- [x] #2 Tests cover first-hour, second-hour, and subsequent-hour rates.
- [x] #3 Tests cover floating hourly blocks that start at the entry timestamp.
- [x] #4 Tests cover partial peak overlap causing the whole block to receive the peak multiplier.
- [x] #5 Tests cover inclusive peak starts and exclusive peak ends.
- [x] #6 Tests cover public holidays disabling weekday peak surcharge behavior.
- [x] #7 Tests cover vehicle multipliers for motorcycle, car, and bus under Standard Hourly.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Audit existing Standard Hourly coverage in src/parking/tests.py and pricing.py behavior (constants, peak windows, rounding, vehicle multipliers). 2. Add focused unit tests in src/parking/test_standard_hourly.py covering all seven ACs: upward rounding, progressive rates, floating blocks from entry timestamp, partial peak overlap -> whole-block multiplier, inclusive peak start / exclusive peak end, public holiday disabling peak, vehicle multipliers (motorcycle/car/bus). 3. Use direct policy evaluation (StandardHourlyPolicy) plus at least one DB-backed calculator check where holiday data is needed. 4. Verify: cd src && uv run python manage.py check && uv run python manage.py test (all green).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Subagent instructions (as-is):

You are implementing Backlog task TASK-5.1 "Test Standard Hourly pricing scenarios" in the Django project at /workspace/smart-parking-lot-v2. This is a TEST-ONLY task: add tests, do not change production code (models, pricing, services, views). If you believe a test reveals a genuine bug in pricing.py, DO NOT fix it — report it in your final report instead.

CONTEXT TO READ FIRST (use the read tool):
- specs/PRD1.md and specs/SRS1.md (Standard Hourly rules and worked examples)
- src/parking/pricing.py (StandardHourlyPolicy, constants: STANDARD_FIRST_HOUR_RATE 5.00, STANDARD_SECOND_HOUR_RATE 3.00, STANDARD_SUBSEQUENT_HOUR_RATE 2.00, PEAK_MULTIPLIER 1.5, PEAK_WINDOWS 7:00-10:00 and 16:00-19:00 with inclusive start / exclusive end, is_weekday_excluding_public_holidays, _rounded_hours, _block_overlaps_peak, quantize_currency)
- src/parking/models.py (PublicHoliday, Vehicle, VehicleType, ParkingSession)
- src/parking/tests.py (existing coverage and test conventions — audit which Standard Hourly cases are ALREADY covered so you fill gaps rather than duplicate)

ACCEPTANCE CRITERIA — each needs at least one dedicated, clearly-named test:
1. Upward rounding to full hours (e.g. 1h01m -> 2 blocks; exact whole hours do not over-round).
2. First-hour ($5.00), second-hour ($3.00), and subsequent-hour ($2.00) rates, including a multi-hour stay hitting all three.
3. Floating hourly blocks that start at the entry timestamp (block boundaries are entry+N hours, not clock-hour aligned; verify via the per-hour block details).
4. Partial peak overlap causes the WHOLE block to receive the 1.5x peak multiplier (e.g. a block 09:30-10:30 overlaps the 7-10 peak only partially).
5. Inclusive peak starts and exclusive peak ends (block ending exactly at 10:00 is peak; block starting exactly at 10:00 is not; same logic for 16:00/19:00 boundaries).
6. Public holidays disable weekday peak surcharge (same weekday+time on a PublicHoliday date -> no 1.5x; also verify a weekend day has no peak).
7. Vehicle multipliers under Standard Hourly: motorcycle 0.8, car 1.0, bus 2.0 (verify the per-block math, e.g. first hour car $5.00, motorcycle $4.00, bus $10.00 off-peak).

IMPLEMENTATION REQUIREMENTS:
- Create src/parking/test_standard_hourly.py.
- Prefer direct unit tests calling StandardHourlyPolicy().evaluate() with lightweight session objects (simple namespace objects with entered_at/exited_at/vehicle are fine — check how existing tests build them and follow convention). Use DB-backed tests (TestCase) only where PublicHoliday rows are required (AC6).
- Use naive or timezone-aware datetimes consistently with the rest of the suite; pick weekday dates deliberately (compute from a known date rather than hardcoding day-of-week assumptions that could drift — or use fixed ISO dates with comments stating the weekday).
- Assert exact Decimal amounts and, where useful, the per-hour block details (peak flag, multipliers, amounts).
- Do NOT modify anything under backlog/, do NOT use Podman/Docker, do NOT modify production code.

TESTING (mandatory):
  cd /workspace/smart-parking-lot-v2/src && uv run python manage.py check
  cd /workspace/smart-parking-lot-v2/src && uv run python manage.py test
All tests (existing 86 + your new ones) must pass and check must be clean. Fix and re-run until green.

FINAL REPORT:
Summarize: which ACs were already partially covered before, files created, test count added, any suspected pricing bugs found (do not fix), and the final check + test output.

Finalization verification (2026-09-28): 'uv run python manage.py check' -> no issues. 'uv run python manage.py test' -> Ran 110 tests, OK. AC evidence from parking.test_standard_hourly (24 tests, all ok): AC1 StandardHourlyRoundingTests (4 tests incl. exact whole hours no over-round); AC2 StandardHourlyBaseRateTests (// tiers + multi-hour all-three); AC3 StandardHourlyFloatingBlockTests (entry+N boundaries, PRD 06:30 example); AC4 StandardHourlyPartialPeakOverlapTests (whole-block 1.5x on partial overlap); AC5 StandardHourlyPeakBoundaryTests (inclusive starts, exclusive ends, morning + evening windows); AC6 StandardHourlyPeakDayRulesTests (holiday disables peak, weekend flat); AC7 StandardHourlyVehicleMultiplierTests (0.8/1.0/2.0 + peak combination). No pricing bugs found; cosmetic note: audit details serialize combined multipliers as '1.50'/'0.80' vs raw '1.5'.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added 24 focused Standard Hourly tests in parking/test_standard_hourly.py covering all seven acceptance criteria: upward rounding, progressive // rates, floating entry-anchored hourly blocks, whole-block peak multiplier on partial overlap, inclusive peak starts / exclusive peak ends, public-holiday and weekend peak exclusion, and motorcycle/car/bus multipliers. Test-only change; no pricing bugs found. Verified with full suite at 110 tests OK and manage.py check clean via direct 'uv run python manage.py' (no Podman).
<!-- SECTION:FINAL_SUMMARY:END -->
