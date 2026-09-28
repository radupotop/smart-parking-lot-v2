---
id: TASK-6
title: 'Task 0: Bootstrap Python environment with uv'
status: To Do
assignee: []
created_date: '2026-09-28 16:13'
labels:
  - backend
  - python
  - uv
  - setup
dependencies: []
references:
  - specs/SRS2.md
priority: high
type: task
ordinal: 0
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Before the Django application shell is created, the repository needs a Python project root under src/ with uv-managed environment setup. The virtual environment should be bootstrapped from inside src/ using the exact requested uv command and paired with a pyproject.toml so later Django and DRF dependency work has a standard project file to build on.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A src/ directory is used as the Python project root for this application.
- [ ] #2 src/ contains a pyproject.toml file with baseline project metadata suitable for later Django and DRF dependencies.
- [ ] #3 The virtual environment bootstrap command is documented or scripted exactly as uv venv --seed --clear --no-managed-python and is intended to run from inside src/.
- [ ] #4 Running the command from src/ creates a local virtual environment for the project without using a uv-managed Python installation.
- [ ] #5 Generated virtual environment files are excluded from git.
<!-- AC:END -->
