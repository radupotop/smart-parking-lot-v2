---
id: TASK-1.5
title: Update Python and Django runtime versions
status: Done
assignee:
  - '@codex'
created_date: '2026-09-28 19:48'
updated_date: '2026-09-28 19:59'
labels:
  - backend
  - django
  - container
  - setup
dependencies:
  - TASK-1.4
references:
  - specs/SRS2.md
modified_files:
  - Containerfile
  - src/pyproject.toml
  - src/uv.lock
  - src/README.md
parent_task_id: TASK-1
priority: high
type: chore
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The project bootstrap currently targets Python 3.12 and Django 5.2. This follow-up keeps the SRS2 Django DRF, SQLite, admin, tests, and Podman runtime aligned with the requested runtime stack: Python 3.14-slim and Django 6.1. The implementation should update both local uv development and container execution paths so future domain work runs against the same versions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The Python runtime base image uses `python:3.14-slim` or the current equivalent slim tag for Python 3.14.
- [x] #2 `src/pyproject.toml` requires Python 3.14 and Django 6.1-compatible dependencies while preserving DRF support.
- [x] #3 `src/uv.lock` is refreshed from the updated dependency constraints.
- [x] #4 Host-side Django check and tests pass through the uv workflow after the upgrade.
- [x] #5 The Podman image builds successfully and the containerized Django check or tests pass.
- [x] #6 Compose runtime configuration and docs, if present, still use the upgraded image/runtime and mounted SQLite path.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the current Containerfile, compose runtime config, pyproject constraints, uv lockfile, README, and existing Django tests/settings.
2. Update the Python runtime image to Python 3.14 slim and adjust pyproject constraints for Python 3.14 plus Django 6.1-compatible DRF support.
3. Refresh uv.lock from the updated constraints, then update docs if version-specific wording is present.
4. Verify host uv Django check/tests, Podman build, containerized check/tests, and compose SQLite/image configuration where the local environment supports it.
5. Record implementation notes and only check acceptance criteria with objective command evidence.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Updated Containerfile to python:3.14-slim and pyproject constraints to Python >=3.14, django>=6.1,<6.2, djangorestframework>=3.18,<4.0. Refreshed uv.lock with `UV_CACHE_DIR=/tmp/uv-cache uv lock`, resolving Django 6.1.1 and DRF 3.18.1.
Verified host stack with `UV_CACHE_DIR=/tmp/uv-cache uv run python -c "import django, rest_framework, sys; ..."` -> Python 3.14.7 / Django 6.1.1 / DRF 3.18.1, `uv run python manage.py check` -> no issues, and `uv run python manage.py test` -> 1 test OK. Verified container stack with `podman build -t smart-parking-lot -f Containerfile .` -> success from python:3.14-slim and `podman run --rm smart-parking-lot uv run python manage.py check` -> no issues. Verified compose with `podman compose config`, showing image smart-parking-lot, Containerfile build, port 8000:8000, DJANGO_SQLITE_PATH=/app/data/db.sqlite3, and ./data bind mounted to /app/data with :Z.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated the Django runtime stack to Python 3.14 slim and Django 6.1 while preserving DRF support. Refreshed uv.lock, documented the Python 3.14 local interpreter expectation, and verified host uv check/tests plus Podman build, containerized Django check, and compose runtime configuration.
<!-- SECTION:FINAL_SUMMARY:END -->
