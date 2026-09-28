---
id: TASK-1.2
title: 'Configure SQLite, DRF, admin, and test runner'
status: To Do
assignee: []
created_date: '2026-09-28 16:02'
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
- [ ] #1 SQLite is the default configured database for local development.
- [ ] #2 Django REST Framework is installed and included in project settings.
- [ ] #3 The admin application is enabled with required middleware, template, and URL configuration.
- [ ] #4 A documented project test command runs an initial passing unit test.
<!-- AC:END -->
