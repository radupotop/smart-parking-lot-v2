# Project Review: smart-parking-lot-v2

## 1. Specs (`specs/`)

| Doc | Verdict |
|---|---|
| **PRD1.md** | The authoritative business spec. Three vehicle classes with multipliers (0.8/1.0/2.0), three policies (Standard Hourly with floating hourly blocks + 1.5x weekday peak surcharge, Early Bird $15, Night Owl $8), loyalty discounts (10/20/30%), best-value conflict resolution, and the >24h special-invalidation rule. Well-specified with a worked example. |
| **SRS1.md** | Design rationale: relational data for facts, Python policy classes for pricing behavior, `RateEvaluation` as a first-class audit record, loyalty-tier snapshot on the session. Sound architecture; the implementation follows it closely. |
| **SRS2.md** | Implementation constraints: Django DRF + SQLite + admin + unit tests + Podman with separate app/test/migrate services. All satisfied. |
| **ERD1.md** | Matches `models.py` field-for-field (7 models, unique constraints, FK/M2M notes). ERD.md is just the template. |

Minor spec-level notes:

- PRD never defines the NONE loyalty tier; SRS1 fills the gap (0% discount) — reasonable.
- SRS1's `PricingPlan` versioned-rate-config idea was deliberately deferred to code constants — explicitly allowed by SRS1 ("for an exercise").

## 2. Backlog (`backlog/`)

- **23 tasks, all Done**, with complete acceptance criteria (all checked), plans, and implementation notes. Good decomposition: bootstrap → models → pricing → workflow/API → tests.
- Tasks reference the spec files, dependencies form a clean DAG (1→2→3→4→5).
- No open drafts/decisions/milestones. (The `backlog search` remote-fetch error is environmental — no `ssh` in this container — not a project issue.)
- Naming quirk: `TASK-6 - Task 0: Bootstrap Python environment with uv` — the "Task 0" vestige is confusing.

## 3. Source (`src/`) — Django 6.1 / DRF / Python 3.14

**Test run (via subagent):** `uv run python manage.py test` → **145 tests, all passing** in 0.64s.

### Strengths

- **`models.py`** — exact match to ERD1; `loyalty_tier_snapshot` on the session (historical billing integrity), `PROTECT` on session FKs, unique constraints on spot `(level, number)` and compatibility pairs.
- **`pricing.py`** — the core is solid:
  - `Decimal` throughout with `ROUND_HALF_UP` cent quantization (no float money).
  - Floating hourly blocks from entry time, round-up to whole hours via exact microsecond math.
  - Partial-peak-overlap with inclusive-start/exclusive-end windows, multi-day block handling, public-holiday exclusion — matches the PRD's 6:30→8:30 example ($12.00) exactly.
  - >24h invalidation uses strict `>` (exactly 24h still qualifies — matches "more than 24 hours").
  - Calculator runs *all* policies, persists one `RateEvaluation` per policy with JSON audit `details`, selects the minimum with a deterministic tie-break (amount → policy order → pk), inside `transaction.atomic()` with `select_for_update`, and re-runs delete stale evaluations (idempotent).
- **`services.py`** — entry validates spot/vehicle compatibility, snapshots loyalty tier; exit is idempotent on closed sessions, rolls back entirely when no policy applies (session stays open).
- **`views.py`/`serializers.py`** — deliberately narrow write surface: sessions only allow GET/POST (create + `exit` action); clients can never write `status`, `charged_amount`, or evaluations. Clean error mapping (400 validation/incompatible spot, 422 no applicable policy).
- **Tests** — 145 tests with strong boundary coverage (05:59/06:00/08:59:59/09:00, 15:30/19:00, 18:00/23:59, 05:00/10:00, 24h±1s, holiday vs weekday, tie-breaks, idempotency, rollback).
- **Ops** — Containerfile (uv + python:3.14-slim), compose with app/test/migrate services and a volume-mounted SQLite path via `DJANGO_SQLITE_PATH`; `.gitignore` correctly excludes `db.sqlite3`, `data/`, caches.

### Issues / gaps (in rough order of importance)

1. **No spot-occupancy tracking.** Nothing prevents two *open* sessions from using the same spot (or a vehicle from having two open sessions). The PRD doesn't explicitly demand occupancy control, but it's the most obvious real-world gap.
2. **Holiday lookup N+1.** `is_weekday_excluding_public_holidays()` runs a DB query per hourly block per date; SRS1 explicitly suggested caching holidays outside the loop. Fine at this scale, but worth fixing if a 48h stay is common.
3. **No API authentication/permissions.** DRF defaults (`AllowAny`) on all endpoints, plus `DEBUG = True` and an insecure `SECRET_KEY` in `settings.py`. Acceptable for the exercise scope, but it's not deployable as-is.
4. **Test duplication.** The legacy monolith `tests/tests.py` (1131 lines) overlaps heavily with the newer split modules (`test_standard_hourly.py`, `test_special_rates.py`, etc.) — e.g. PRD floating example and holiday tests exist in both. Harmless, but it doubles maintenance surface; consider consolidating.
5. **`exited_at` before `entered_at` via API** yields a 422 with the session left open — correct behavior, but the error message ("No applicable rate policy...") is less helpful than a plain "exited_at must be after entered_at" 400.
6. **`record_entry` doesn't prevent a vehicle with an existing open session** from entering again (same root cause as #1).
7. Cosmetic: `HOUR_MICROSECONDS`/manual microsecond ceil is correct but `math.ceil(duration.total_seconds() / 3600)` with a tiny epsilon would be simpler; `TimeWindow` raising `ValueError` for `start > end` is dead-code protection (no window wraps midnight).

### Verdict

The implementation is a faithful, well-tested realization of the specs: every PRD rule (floating blocks, partial peak overlap, inclusive/exclusive boundaries, loyalty + vehicle multipliers, best-value selection, >24h invalidation, audit trail) is implemented and pinned down by boundary tests, and all 23 backlog tasks are legitimately complete. The main future work is operational hardening: spot occupancy, auth, holiday caching, and test deduplication.
