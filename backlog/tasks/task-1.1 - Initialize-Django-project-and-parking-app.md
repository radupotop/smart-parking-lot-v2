---
id: TASK-1.1
title: Initialize Django project and parking app
status: Done
assignee:
  - '@codex'
created_date: '2026-09-28 16:02'
updated_date: '2026-09-28 18:53'
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
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The application needs a conventional Django project structure before the parking domain can be implemented. This subtask creates the project shell and a local app dedicated to the smart parking lot domain.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A Django project package exists with settings, URL configuration, and WSGI or ASGI entrypoint.
- [x] #2 A local parking-domain app exists and is registered in installed apps.
- [x] #3 The project can start without import or settings errors.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect src/ and pyproject.toml to understand the existing uv project root.
2. Add a conventional Django project package and manage.py under src/.
3. Add a local parking-domain app package and register it in project settings.
4. Keep database/admin/DRF/test-runner details minimal here so TASK-1.2 can configure them.
5. Verify the project imports and can run a Django startup check without import/settings errors.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented the Django project shell under src/ with manage.py, config settings/URL/ASGI/WSGI modules, and a parking app registered in INSTALLED_APPS. Verified with uv run python manage.py check from src/ after allowing uv cache access; Django reported no system check issues.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Created the src Django project shell with manage.py, config settings/URL/ASGI/WSGI modules, and the registered parking app. Verified startup with uv run python manage.py check from src/, which reported no system check issues.
<!-- SECTION:FINAL_SUMMARY:END -->
