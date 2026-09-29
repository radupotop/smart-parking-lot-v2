# GPT Review: smart-parking-lot-v2

## Scope

Reviewed the Django/DRF parking billing project against the product and system
requirements in `specs/`, the current implementation under `src/`, the API and
service tests, the container setup, and the existing backlog/task history.

Verification run:

```sh
podman compose run --rm test
```

Result: 182 tests passed inside the Podman test service.

## Overall Assessment

This is a strong implementation of the exercise requirements. The pricing
engine closely follows the PRD: it uses `Decimal` money arithmetic, floating
hourly blocks, partial peak overlap detection, weekday/public-holiday handling,
vehicle multipliers, loyalty discounts, special-rate invalidation after 24
hours, exhaustive policy evaluation, and best-value selection.

The model shape is also well chosen for auditability. `ParkingSession` acts as
the ticket, snapshots the billing context, and links to persisted
`RateEvaluation` rows so the system can explain which policies were considered
and why the winning price was selected.

The main gaps are not in the rate math. They are in operational workflow
invariants and API hardening.

## Findings

### 1. Open sessions can double-book the same spot or vehicle

Severity: High

`record_entry()` validates spot/vehicle compatibility, then creates an open
session directly (`src/parking/services.py:65` and `src/parking/services.py:78`).
`ParkingSession` has no database constraint preventing multiple open sessions
for the same `spot` or the same `vehicle` (`src/parking/models.py:111`).

This means the API can create two active tickets for one physical spot, or issue
two active tickets for the same vehicle. The current session API tests even
create two open sessions against the same spot while verifying ordering
(`src/parking/tests/test_api_sessions.py:175`).

Recommendation: add open-session occupancy rules at both levels:

- database constraints such as conditional unique constraints for
  `(spot)` where `status="open"` and `(vehicle)` where `status="open"`;
- service-level validation with clear domain errors and API 400 responses;
- tests for duplicate open spot and duplicate open vehicle entry attempts.

### 2. Protected delete handling is inconsistent across resources

Severity: Medium

`ParkingSpotViewSet.destroy()` catches `ProtectedError` and returns a readable
400 when a referenced spot cannot be deleted (`src/parking/views.py:67`). The
same protection is not present for customers or vehicles
(`src/parking/views.py:41` and `src/parking/views.py:48`), even though
`ParkingSession.vehicle` and `ParkingSession.customer` both use `PROTECT`
(`src/parking/models.py:112` and `src/parking/models.py:122`).

A DELETE request for a vehicle or customer referenced by a session is likely to
surface as an unhandled server error instead of a client-safe validation
response.

Recommendation: share the protected-delete handling through a small mixin or
override `destroy()` on `CustomerViewSet` and `VehicleViewSet` as well. Add API
tests mirroring the existing protected spot delete coverage.

### 3. Exit timestamps before entry are reported as pricing failures

Severity: Medium

When `exited_at <= entered_at`, the pricing policies mark themselves
inapplicable (`src/parking/pricing.py:146` and `src/parking/pricing.py:310`).
The API maps the resulting `NoApplicableRatePolicyError` to HTTP 422
(`src/parking/views.py:146`). Tests currently pin this behavior
(`src/parking/tests/test_api_session_exit.py:120`).

The rollback behavior is good, but this is input validation rather than "no
pricing policy matched." A caller gets a less actionable error than a direct
`exited_at must be after entered_at` 400.

Recommendation: validate the exit timestamp in `SessionExitSerializer` or
`record_exit()` before invoking the calculator, return 400, and keep the
existing rollback/no-state-change behavior.

### 4. Public-holiday checks query inside the hourly loop

Severity: Low

`StandardHourlyPolicy.evaluate()` iterates one block per rounded hour
(`src/parking/pricing.py:163`) and `_block_overlaps_peak()` calls
`is_weekday_excluding_public_holidays()` for each date touched by the block
(`src/parking/pricing.py:230`). That helper performs a database `.exists()`
query every time (`src/parking/pricing.py:124`).

This is fine for the exercise and normal short stays, but longer sessions
produce unnecessary repeated queries for the same dates.

Recommendation: prefetch the holiday dates for the session date range once per
standard-hourly evaluation and pass a set into the peak-day check.

### 5. Runtime settings are intentionally development-only

Severity: Low

`SECRET_KEY` is hard-coded, `DEBUG=True`, `ALLOWED_HOSTS=[]`, and the API uses
DRF's default open access (`src/config/settings.py:9`). This is acceptable for a
coding exercise and local Podman workflow, but it is not deployable as a real
service.

Recommendation: if this project is promoted beyond the exercise, move secrets
and debug settings to environment variables and add authentication/permissions
for operational endpoints.

### 6. Tests are comprehensive but duplicated

Severity: Low

The suite is broad and valuable, but the legacy monolithic
`src/parking/tests/tests.py` overlaps with the newer focused files such as
`test_standard_hourly.py`, `test_special_rates.py`, and API-specific modules.
The test run is still very fast, so this is a maintenance concern rather than a
delivery blocker.

Recommendation: keep the focused modules as the long-term structure and retire
duplicated cases from the monolith when making future changes.

## Strengths

- Pricing rules are faithful to the PRD, including tricky boundary behavior.
- Billing uses `Decimal` and explicit cent quantization.
- The audit model is excellent for explaining charges and debugging disputes.
- Exit is idempotent for already-closed sessions.
- Failed exits roll back cleanly and leave sessions open.
- Compatibility defaults are seeded through an idempotent migration.
- The containerized test service works and the full suite passes.

## Verdict

The project is functionally complete for the stated pricing exercise. The next
highest-value work is to enforce live occupancy invariants, normalize protected
delete handling, and improve timestamp validation at session exit. After that,
holiday caching and test deduplication would be tidy follow-up work.
