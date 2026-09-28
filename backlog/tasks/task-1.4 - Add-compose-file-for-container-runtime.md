---
id: TASK-1.4
title: Add compose file for container runtime
status: To Do
assignee: []
created_date: '2026-09-28 19:08'
labels:
  - backend
  - podman
  - container
  - compose
dependencies: []
references:
  - specs/SRS2.md
parent_task_id: TASK-1
priority: medium
type: task
ordinal: 21000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The current Podman runtime is documented as individual build, run, migrate, and test commands. A compose YAML should capture that container infrastructure in one reusable configuration so future agents and developers can start the app with mounted SQLite storage without reconstructing the command line by hand.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A compose YAML file exists at the repository root using the current Containerfile-based Django image.
- [ ] #2 The compose configuration mounts a host directory for SQLite persistence at the container data path used by the app.
- [ ] #3 The compose configuration exposes the Django development server on host port 8000.
- [ ] #4 The compose configuration sets any required environment variables, including the SQLite database path used in the container.
- [ ] #5 Documentation explains how to build/start the app, run migrations, and run tests through the compose workflow.
- [ ] #6 Generated compose/runtime artifacts remain ignored by git.
<!-- AC:END -->
