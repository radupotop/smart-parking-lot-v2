---
id: TASK-1.3
title: Add Podman container runtime
status: Done
assignee:
  - '@codex'
created_date: '2026-09-28 16:02'
updated_date: '2026-09-28 19:02'
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
- [x] #1 A Containerfile or equivalent Podman-compatible image definition can run the Django app.
- [x] #2 A documented Podman command or compose-compatible configuration starts the app locally.
- [x] #3 The runtime mounts the SQLite database file or containing directory from the host filesystem.
- [x] #4 Container documentation explains how to run migrations, run tests, and start the development server.
- [x] #5 Generated database files and other runtime artifacts are ignored by git where appropriate.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the current Django/uv project layout and runtime requirements.
2. Add a Podman-compatible Containerfile for the Django app.
3. Add documented Podman commands or compose-compatible configuration to run the app locally.
4. Ensure the runtime mounts a host SQLite database path into the container.
5. Document container commands for migrations, tests, and development server startup.
6. Ignore generated database/runtime artifacts and verify the container configuration by inspection and available Podman checks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added a Podman-compatible Containerfile, .containerignore, runtime docs, DJANGO_SQLITE_PATH support for mounted SQLite storage, and ignore rules for generated database/runtime artifacts. Verified podman --version, podman build, containerized migrate with /tmp/smart-parking-lot-data mounted at /app/data, containerized tests, and host uv run check/test.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added the Podman runtime and documentation for build, run, migrate, test, and development server commands. Verified the image builds, migrations run with mounted SQLite storage, container tests pass, and generated runtime artifacts are ignored.
<!-- SECTION:FINAL_SUMMARY:END -->
