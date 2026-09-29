---
id: TASK-9
title: Seed default spot and vehicle compatibility pairs
status: Done
assignee:
  - '@codex'
created_date: '2026-09-29 14:29'
updated_date: '2026-09-29 14:32'
labels: []
dependencies: []
type: bug
ordinal: 30000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Posting a motorcycle into a compact spot through /api/sessions/ returns an incompatible-spot 400 unless an operator has manually inserted SpotTypeVehicleCompatibility rows. The spec says compact spots accommodate motorcycles and cars, so a fresh migrated database should include the default compatibility facts needed for normal ticket entry.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A fresh migrated database contains the default compact/motorcycle and compact/car compatibility pairs
- [x] #2 Large spots contain the default bus compatibility pair for the fixed vehicle classes
- [x] #3 Re-running migrations or applying the seed to an existing database does not create duplicate compatibility rows
- [x] #4 Tests cover session creation for a motorcycle in a compact spot without per-test manual compatibility setup
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add an idempotent Django data migration that seeds fixed default SpotTypeVehicleCompatibility rows for the built-in spot and vehicle classes.
2. Add focused test coverage proving the defaults exist in the test database and /api/sessions/ accepts a motorcycle in a compact spot without manually creating a compatibility row.
3. Run Django checks and the relevant/full test suite, then finalize TASK-9 with evidence.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented src/parking/migrations/0003_seed_default_spot_vehicle_compatibilities.py with idempotent get_or_create seeding for compact/motorcycle, compact/car, and large/bus. Updated tests to rely on migrated default compatibility data instead of manually creating compact/car fixture rows, and added a regression test for POST /api/sessions/ with a motorcycle in a compact spot.

Validation: UV_CACHE_DIR=/tmp/uv-cache uv run python manage.py makemigrations --check --dry-run -> no changes; uv run python manage.py check -> no issues; focused compatibility/session tests ran 15 tests OK; full uv run python manage.py test ran 182 tests OK. Applied parking.0003 migration to both src/db.sqlite3 and data/db.sqlite3; both now contain compact/car, compact/motorcycle, and large/bus exactly once.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Seeded default spot/vehicle compatibility facts with an idempotent Django data migration so fresh and existing databases allow normal compact motorcycle/car entry and large bus entry without manual admin setup. Updated fixtures and added regression coverage for POST /api/sessions/ with a motorcycle in a compact spot. Verified migration drift, Django system check, focused tests, full 182-test suite, and local src/data SQLite migration state.
<!-- SECTION:FINAL_SUMMARY:END -->
