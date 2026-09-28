---
id: TASK-1
title: Bootstrap Django DRF application shell
status: Done
assignee:
  - '@codex'
created_date: '2026-09-28 15:51'
updated_date: '2026-09-28 20:01'
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
Completed all five child tasks: TASK-1.1 project/app shell, TASK-1.2 SQLite/DRF/admin/test runner, TASK-1.3 Podman runtime, TASK-1.4 compose runtime workflow, and TASK-1.5 Python 3.14/Django 6.1 runtime upgrade. Final verification passed with uv lock consistency, uv Django check/test commands, Podman image build, containerized Django check, and Podman Compose config for the mounted SQLite runtime.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Bootstrapped the Django DRF application shell with SQLite, admin, tests, Podman runtime support, a compose workflow, and the requested Python 3.14 slim / Django 6.1 stack. Verified host uv checks/tests plus Podman build, containerized Django check, and compose configuration.
<!-- SECTION:FINAL_SUMMARY:END -->
