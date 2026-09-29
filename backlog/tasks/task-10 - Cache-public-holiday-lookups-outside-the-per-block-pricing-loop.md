---
id: TASK-10
title: Cache public holiday lookups outside the per-block pricing loop
status: To Do
assignee: []
created_date: '2026-09-29 23:49'
labels: []
dependencies: []
references:
  - QWEN_REVIEW.md
  - specs/SRS1.md
ordinal: 31000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
QWEN_REVIEW.md issue 2: is_weekday_excluding_public_holidays() in src/parking/pricing.py runs a PublicHoliday.objects.filter(...).exists() DB query for every hourly block of a Standard Hourly evaluation, once per distinct date. A 48h stay issues up to ~48 queries for the same handful of dates. SRS1 explicitly suggested caching/fetching holidays outside the calculation loop. Behaviour must stay identical (weekdays are Mon-Fri excluding configured public holidays); only the query pattern changes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Standard Hourly evaluation issues at most one PublicHoliday query per evaluation (or per distinct date), not one per hourly block
- [ ] #2 Pricing results are unchanged: full existing test suite passes without assertion edits
- [ ] #3 Tests assert the reduced query count for a multi-day (e.g. 48h) session using Django assertNumQueries or equivalent
- [ ] #4 Holiday exclusion still works when a block spans midnight and when a holiday falls on an interior date of a multi-day stay
<!-- AC:END -->
