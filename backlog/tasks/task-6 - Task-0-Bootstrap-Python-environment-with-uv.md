---
id: TASK-6
title: 'Task 0: Bootstrap Python environment with uv'
status: Done
assignee:
  - '@codex'
created_date: '2026-09-28 16:13'
updated_date: '2026-09-28 18:46'
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
- [x] #1 A src/ directory is used as the Python project root for this application.
- [x] #2 src/ contains a pyproject.toml file with baseline project metadata suitable for later Django and DRF dependencies.
- [x] #3 The virtual environment bootstrap command is documented or scripted exactly as uv venv --seed --clear --no-managed-python and is intended to run from inside src/.
- [x] #4 Running the command from src/ creates a local virtual environment for the project without using a uv-managed Python installation.
- [x] #5 Generated virtual environment files are excluded from git.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the repository layout and existing ignore/configuration files.
2. Create src/ as the Python project root with pyproject.toml baseline metadata for the Django/DRF app.
3. Add a small bootstrap entry point or documentation that runs uv venv --seed --clear --no-managed-python from inside src/.
4. Ensure generated virtual environment files under src/ are ignored by git.
5. Verify with file inspection and the uv venv command when available.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented the src/ Python project root with pyproject.toml, README bootstrap instructions, and .gitignore coverage for generated virtual environments. Verified uv venv --seed --clear --no-managed-python from src/ after allowing uv cache access; src/.venv/pyvenv.cfg exists and is ignored by git.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Created src/ as the Python project root with pyproject.toml and README bootstrap instructions. Verified uv venv --seed --clear --no-managed-python from src/, confirmed src/.venv/pyvenv.cfg exists, and confirmed git ignores the generated venv.
<!-- SECTION:FINAL_SUMMARY:END -->
