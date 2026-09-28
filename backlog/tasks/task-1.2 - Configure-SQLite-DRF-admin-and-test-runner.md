---
id: TASK-1.2
title: 'Configure SQLite, DRF, admin, and test runner'
status: Done
assignee:
  - '@codex'
created_date: '2026-09-28 16:02'
updated_date: '2026-09-28 18:56'
labels:
  - backend
  - django
  - setup
dependencies: []
references:
  - specs/SRS2.md
parent_task_id: TASK-1
priority: high
type: task
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
SRS2 expects SQLite, Django REST Framework, the Django admin, and unit tests to be available early. This subtask wires the shared project configuration that later model, API, and test tasks rely on.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 SQLite is the default configured database for local development.
- [x] #2 Django REST Framework is installed and included in project settings.
- [x] #3 The admin application is enabled with required middleware, template, and URL configuration.
- [x] #4 A documented project test command runs an initial passing unit test.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the current Django shell from TASK-1.1.
2. Configure SQLite explicitly for local development and keep database artifacts out of git.
3. Add Django REST Framework as a dependency and register it in settings.
4. Ensure Django admin prerequisites remain enabled through installed apps, middleware, templates, and URLs.
5. Add a minimal documented test command and initial passing unit test.
6. Verify with Django system checks and the project test command.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Configured DRF in pyproject/settings, confirmed SQLite remains the default local database, preserved admin app/middleware/template/URL wiring, added SQLite DB ignore rules, documented the test command, and added a passing admin route smoke test. Verified with uv run python manage.py check and uv run python manage.py test from src/.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Configured SQLite/DRF/admin/test-runner basics and documented uv run python manage.py test. Verified Django system checks pass and the documented test command runs 1 passing test.
<!-- SECTION:FINAL_SUMMARY:END -->
