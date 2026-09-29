---
id: TASK-7
title: Add API tests for each API endpoint
status: To Do
assignee: []
created_date: '2026-09-29 11:08'
labels:
  - backend
  - api
  - tests
dependencies: []
references:
  - specs/SRS2.md
priority: medium
type: feature
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
SRS2 deferred API test expansion ("api tests to be added later") and the existing test_api.py only has initial coverage mixed with the TASK-4 work. This initiative adds dedicated, organized API test coverage for every DRF endpoint under /api/, one subtask per endpoint. To keep the suite focused and fast, each endpoint is capped at 5 tests covering its most important behaviors (happy path, key validation errors, and endpoint-specific rules).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Every API endpoint (customers, vehicles, spots, sessions, sessions exit) has a dedicated test module
- [ ] #2 Each endpoint test module contains no more than 5 tests
- [ ] #3 The full test suite passes with the new API tests
<!-- AC:END -->
