---
id: TASK-1
title: Bootstrap Django DRF application shell
status: Done
assignee:
  - '@codex'
created_date: '2026-09-28 15:51'
updated_date: '2026-09-28 19:03'
labels:
  - backend
  - django
  - setup
dependencies:
  - TASK-6
references:
  - specs/SRS2.md
priority: high
type: feature
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
SRS2 calls for a simple Django DRF application backed by SQLite, with the Django admin enabled, unit tests available from the start, and a Podman runtime where the SQLite database file can be mounted from the local filesystem. This task establishes the application skeleton so the parking domain and billing engine have a conventional place to live.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The repository contains a runnable Django project with at least one local app for the parking domain.
- [x] #2 SQLite is configured as the default database for local development.
- [x] #3 Django REST Framework is installed and wired into the project settings.
- [x] #4 The Django admin site is enabled and reachable when the development server runs.
- [x] #5 The project test command runs successfully with an initial unit test.
- [x] #6 Podman configuration can run the app and mount the SQLite database file from the host filesystem.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Completed all three child tasks: TASK-1.1 project/app shell, TASK-1.2 SQLite/DRF/admin/test runner, and TASK-1.3 Podman runtime. Final parent verification passed with uv run python manage.py check, uv run python manage.py test, Podman image build, mounted SQLite migration, and containerized tests.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Bootstrapped the Django DRF application shell with SQLite, admin, tests, and Podman runtime support. Verified host Django check/test commands plus Podman build, mounted SQLite migration, and containerized tests.
<!-- SECTION:FINAL_SUMMARY:END -->
