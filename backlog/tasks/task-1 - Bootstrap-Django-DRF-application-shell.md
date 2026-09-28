---
id: TASK-1
title: Bootstrap Django DRF application shell
status: In Progress
assignee:
  - '@codex'
created_date: '2026-09-28 15:51'
updated_date: '2026-09-28 18:50'
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
- [ ] #1 The repository contains a runnable Django project with at least one local app for the parking domain.
- [ ] #2 SQLite is configured as the default database for local development.
- [ ] #3 Django REST Framework is installed and wired into the project settings.
- [ ] #4 The Django admin site is enabled and reachable when the development server runs.
- [ ] #5 The project test command runs successfully with an initial unit test.
- [ ] #6 Podman configuration can run the app and mount the SQLite database file from the host filesystem.
<!-- AC:END -->
