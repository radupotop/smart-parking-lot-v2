---
id: TASK-1.3
title: Add Podman container runtime
status: To Do
assignee: []
created_date: '2026-09-28 16:02'
labels:
  - backend
  - podman
  - container
dependencies: []
references:
  - specs/SRS2.md
parent_task_id: TASK-1
priority: high
type: task
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
SRS2 explicitly says the app will run in a Podman container and that the SQLite database file should be mounted from the local filesystem. This needs its own implementation task so container behavior is not hidden inside the general Django bootstrap work.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A Containerfile or equivalent Podman-compatible image definition can run the Django app.
- [ ] #2 A documented Podman command or compose-compatible configuration starts the app locally.
- [ ] #3 The runtime mounts the SQLite database file or containing directory from the host filesystem.
- [ ] #4 Container documentation explains how to run migrations, run tests, and start the development server.
- [ ] #5 Generated database files and other runtime artifacts are ignored by git where appropriate.
<!-- AC:END -->
