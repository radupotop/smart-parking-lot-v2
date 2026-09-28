---
id: TASK-1.4
title: Add compose file for container runtime
status: Done
assignee:
  - '@codex'
created_date: '2026-09-28 19:08'
updated_date: '2026-09-28 19:53'
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
- [x] #1 A compose YAML file exists at the repository root using the current Containerfile-based Django image.
- [x] #2 The compose configuration mounts a host directory for SQLite persistence at the container data path used by the app.
- [x] #3 The compose configuration exposes the Django development server on host port 8000.
- [x] #4 The compose configuration sets any required environment variables, including the SQLite database path used in the container.
- [x] #5 Documentation explains how to build/start the app, run migrations, and run tests through the compose workflow.
- [x] #6 Generated compose/runtime artifacts remain ignored by git.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add a root compose YAML that builds the existing Containerfile image, exposes 8000, sets DJANGO_SQLITE_PATH, and bind-mounts ./data to /app/data for SQLite persistence.
2. Update src/README.md with compose build/start, migrate, and test commands while preserving the existing Podman runtime context.
3. Verify compose rendering when a compose implementation is available, run reasonable Django checks/tests, then check acceptance criteria and record completion notes.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added root compose.yaml for the app service using image smart-parking-lot, build context ., Containerfile, port 8000:8000, DJANGO_SQLITE_PATH=/app/data/db.sqlite3, and ./data:/app/data:Z persistence. Updated src/README.md with compose up --build, migrate, test, and down commands. Verification: podman compose config rendered the expected build/image/env/port/bind mount; UV_CACHE_DIR=/tmp/uv-cache uv run python manage.py check passed; UV_CACHE_DIR=/tmp/uv-cache uv run python manage.py test passed (1 test); git check-ignore -v data/ confirms runtime data stays ignored by .gitignore.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added a root Compose-spec configuration for the existing Containerfile-based Django runtime and documented the compose workflow for start, migrations, and tests. Verified with podman compose config, Django system checks/tests via uv using a tmp cache, and git check-ignore for the data/ runtime directory.
<!-- SECTION:FINAL_SUMMARY:END -->
