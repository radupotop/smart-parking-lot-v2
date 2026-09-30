---
id: TASK-10
title: Cache public holiday lookups outside the per-block pricing loop
status: To Do
assignee: []
created_date: '2026-09-29 23:49'
updated_date: '2026-09-30 00:34'
labels: []
dependencies: []
references:
  - QWEN_REVIEW.md
  - specs/SRS1.md
  - src/parking/pricing.py
  - src/parking/tests/test_standard_hourly.py
ordinal: 31000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
QWEN_REVIEW.md, source issue 2 (Holiday lookup N+1), identifies repeated PublicHoliday database lookups during Standard Hourly pricing. StandardHourlyPolicy.evaluate() loops over rounded hourly blocks; _block_overlaps_peak() visits their calendar dates and calls is_weekday_excluding_public_holidays(), which issues an exists() query for each weekday visit. Dates are repeatedly queried across blocks. SRS1.md explicitly recommends fetching/caching holidays outside the calculation loop.

Requirements:
- After validating the evaluation inputs, fetch the relevant holiday dates once into an in-memory set and reuse it throughout that evaluation. Restrict the fetch to the date range visited by the billed hourly blocks, including the final rounded block, which may extend past exited_at and onto another date.
- Perform weekday/holiday checks inside the block/date loop without database queries. Preserve the existing Monday-Friday definition, datetime date/timezone interpretation, floating hourly blocks, half-open overlap boundaries, rounding, vehicle multipliers, amounts, and audit details.
- Keep the holiday set local to each evaluate() call, even when the same policy instance is reused. Holiday additions, date changes, and deletions must be visible on the next evaluation; no persistent or process-wide cache is needed.
- Preserve the existing standalone date/datetime behavior of is_weekday_excluding_public_holidays(). An optional preloaded holiday set is acceptable, but callers without one must retain database-backed behavior.
- Add focused regression tests for query counts, date coverage, and cache freshness. Measure holiday queries separately from fixture setup, session/vehicle loading, and persisted RateEvaluation queries.
- This is a pricing query optimization; it requires no schema migration, API change, external holiday service, or change to the special flat-rate policies.

Relevant code: src/parking/pricing.py; focused tests: src/parking/tests/test_standard_hourly.py and the existing helper tests in src/parking/tests/tests.py. Run the focused tests and full suite inside Podman using the compose test service.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 StandardHourlyPolicy.evaluate() issues at most one PublicHoliday SELECT for a valid evaluation, independent of the number of hourly blocks or dates; no holiday queries occur inside the block/date loop.
- [ ] #2 Holiday fetching is bounded to the calendar dates visited by billed blocks, including the end of the final rounded block rather than only the actual exit date.
- [ ] #3 Existing pricing amounts, per-hour peak flags, audit details, weekday/weekend behavior, timezone interpretation, rounding, and overlap boundaries remain unchanged; the existing full suite passes without changing expected pricing assertions.
- [ ] #4 Focused query-count tests cover a same-day stay and a weekday-spanning multi-day stay of at least 48 hours, asserting at most one holiday query per evaluation with Django assertNumQueries or equivalent; fixture and unrelated ORM queries are excluded.
- [ ] #5 Regression tests cover a block spanning midnight, a holiday on an interior date of a multi-day stay, and a final rounded block crossing into a holiday date; holiday peak exclusion and adjacent non-holiday peak behavior remain correct.
- [ ] #6 Repeated evaluate() calls on the same policy instance see holiday additions, date changes, and deletions made between calls, proving the cache is scoped to one evaluation.
- [ ] #7 The standalone is_weekday_excluding_public_holidays() helper retains its existing date and datetime support and database-backed behavior when no preloaded set is supplied.
- [ ] #8 Inputs rejected before hourly calculation cause no PublicHoliday query and retain their current not-applicable reason and details.
- [ ] #9 Focused tests and the full Django test suite pass inside the Podman compose test service; record the commands and results when implementing the task.
- [ ] #10 Holiday caching uses a plain Python set local to each evaluate() call, discarded after that call; no Django cache, Redis, process-wide cache, or policy-instance cache is used.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Cache mechanism: use a plain Python set of holiday dates held in a local variable within StandardHourlyPolicy.evaluate(). Build it once per evaluation and pass it to the block/date checks for in-memory membership tests. Discard it when evaluation finishes; the next evaluation fetches current holiday data again. Do not use Django's cache framework, Redis, a process-wide cache, or state retained on the policy instance. No cache backend configuration, expiry, or invalidation mechanism is required.

Why local memory addresses the N+1 issue:

The repeated queries happen within one pricing calculation: each hourly block asks the database whether its date is a holiday. A 48-hour stay repeatedly queries the same few dates.

Fetch all holiday dates relevant to the billed blocks with one database query, store them in a Python set, and check each block date against that set. Membership checks run in memory without database access. The number of holiday queries therefore drops from roughly one per weekday block to at most one per evaluation, regardless of the stay's length.

Redis or Django cache would share cached data across separate evaluations or processes. That is unnecessary to resolve repetition within a single evaluation and would introduce cache expiry or invalidation rules when holidays change. Fetching once per evaluation ensures the next calculation sees current holiday data without those mechanisms.

Strictly speaking, this approach is bulk fetching and local reuse rather than a persistent cache.
<!-- SECTION:NOTES:END -->
