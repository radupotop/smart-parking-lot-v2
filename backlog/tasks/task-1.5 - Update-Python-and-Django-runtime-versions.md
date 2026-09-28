---
id: TASK-1.5
title: Update Python and Django runtime versions
status: To Do
assignee: []
created_date: '2026-09-28 19:48'
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
- [ ] #1 The Python runtime base image uses `python:3.14-slim` or the current equivalent slim tag for Python 3.14.
- [ ] #2 `src/pyproject.toml` requires Python 3.14 and Django 6.1-compatible dependencies while preserving DRF support.
- [ ] #3 `src/uv.lock` is refreshed from the updated dependency constraints.
- [ ] #4 Host-side Django check and tests pass through the uv workflow after the upgrade.
- [ ] #5 The Podman image builds successfully and the containerized Django check or tests pass.
- [ ] #6 Compose runtime configuration and docs, if present, still use the upgraded image/runtime and mounted SQLite path.
<!-- AC:END -->
