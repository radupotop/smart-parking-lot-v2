"""Dedicated scenario tests for the Early Bird and Night Owl specials (TASK-5.2).

These tests fill the gaps left by ``SpecialFlatRatePolicyTests`` and
``ParkingRateCalculatorTests`` in ``tests.py`` and pin each acceptance
criterion of TASK-5.2 with a clearly-named test.

Coverage audit of the pre-existing suite (so these tests fill gaps, not
duplicate):
- ``tests.py`` already covers: Early Bird entry 06:00 (in) / 09:00 (out),
  exit 15:30 (in) / 19:00 (out), next-day exit rejection; Night Owl entry
  18:00 (in) / 17:59:59 (out) / 23:59:59 (in), exit 05:00 (in) / 10:00
  (out), same-day exit and two-days-later exit rejection; all four loyalty
  tiers for a car under both specials; two combined loyalty+vehicle cases
  (motorcycle/silver Early Bird, bus/gold Night Owl); 24h+1s invalidation
  of both specials; and one special-wins best-value calculator case.
- Gaps filled here: Early Bird entry 05:59 (out) and cross-midnight
  rejection; Night Owl entry exactly 23:59:00 and exit 04:59:59 (out) /
  09:59:59 (in); the exact-24h boundary semantics; the full
  motorcycle/car/bus multiplier sets under both flat specials; the
  standard-wins and tie-break branches of best-value selection.

Conventions:
- Direct policy tests use lightweight ``SimpleNamespace`` sessions exposing
  only what the special policies read: ``entered_at``, ``exited_at``,
  ``vehicle.vehicle_type`` and ``loyalty_tier_snapshot``. The special
  policies never touch the ORM, so those tests use ``SimpleTestCase``.
- AC6 (best-value selection + persistence) uses DB-backed ``TestCase``
  tests with real ``ParkingSession`` rows and the real
  ``ParkingRateCalculator`` (plus stub policies for the standard-wins and
  tie-break branches, which cannot occur with the real policy parameters --
  see ``SpecialBestValueSelectionTests`` docstring).
- Datetimes are timezone-aware UTC. Fixed ISO dates with weekday comments:
    2026-09-28 -> Monday (weekday)
    2026-09-29 -> Tuesday (weekday)
    2026-09-30 -> Wednesday (weekday)
  The special policies do not depend on weekday/holidays, but the dates are
  kept explicit for readability and for the DB-backed standard-policy math.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

from django.test import SimpleTestCase, TestCase

from parking.models import (
    LoyaltyTier,
    ParkingSession,
    ParkingSpot,
    RateEvaluation,
    RatePolicy,
    SessionStatus,
    SpotType,
    Vehicle,
    VehicleType,
)
from parking.pricing import (
    EarlyBirdPolicy,
    NightOwlPolicy,
    ParkingRateCalculator,
    PolicyResult,
)

# 2026-09-28 is a Monday (verified weekday; used as the "entry day").
MONDAY = date(2026, 9, 28)
# 2026-09-29 is a Tuesday (verified weekday; the next consecutive day).
TUESDAY = date(2026, 9, 29)
# 2026-09-30 is a Wednesday (verified weekday; used for non-consecutive exits).
WEDNESDAY = date(2026, 9, 30)


def _at(day: date, hour: int, minute: int = 0, second: int = 0) -> datetime:
    """Build a timezone-aware UTC datetime on the given day."""

    return datetime(day.year, day.month, day.day, hour, minute, second, tzinfo=timezone.utc)


def _session(
    entered_at: datetime,
    exited_at: datetime,
    vehicle_type: str = VehicleType.CAR,
    loyalty_tier: str = LoyaltyTier.NONE,
) -> SimpleNamespace:
    """Build a lightweight session object for direct special-policy evaluation."""

    return SimpleNamespace(
        entered_at=entered_at,
        exited_at=exited_at,
        vehicle=SimpleNamespace(vehicle_type=vehicle_type),
        loyalty_tier_snapshot=loyalty_tier,
    )


class EarlyBirdWindowBoundaryTests(SimpleTestCase):
    """AC1: Early Bird entry/exit window boundaries and same-day rule.

    Entry window 06:00 (inclusive) - 09:00 (exclusive); exit window
    15:30 (inclusive) - 19:00 (exclusive); entry and exit on the same
    calendar day.
    """

    def setUp(self) -> None:
        self.policy = EarlyBirdPolicy()

    def test_entry_exactly_at_0600_is_included(self) -> None:
        session = _session(_at(MONDAY, 6, 0), _at(MONDAY, 16, 0))

        result = self.policy.evaluate(session)

        self.assertTrue(result.applicable)
        self.assertEqual(result.amount, Decimal("15.00"))
        self.assertEqual(result.details["applicability_reason"], "applicable")

    def test_entry_at_0559_is_excluded(self) -> None:
        session = _session(_at(MONDAY, 5, 59), _at(MONDAY, 16, 0))

        result = self.policy.evaluate(session)

        self.assertFalse(result.applicable)
        self.assertIsNone(result.amount)
        self.assertEqual(result.details["reason"], "entry_time_outside_window")

    def test_entry_exactly_at_0900_is_excluded(self) -> None:
        # 09:00 is the exclusive end of the entry window.
        session = _session(_at(MONDAY, 9, 0), _at(MONDAY, 16, 0))

        result = self.policy.evaluate(session)

        self.assertFalse(result.applicable)
        self.assertIsNone(result.amount)
        self.assertEqual(result.details["reason"], "entry_time_outside_window")

    def test_entry_just_before_0900_is_included(self) -> None:
        # 08:59:59 is the latest representable entry that still qualifies.
        session = _session(_at(MONDAY, 8, 59, 59), _at(MONDAY, 16, 0))

        result = self.policy.evaluate(session)

        self.assertTrue(result.applicable)
        self.assertEqual(result.amount, Decimal("15.00"))

    def test_exit_exactly_at_1530_is_included(self) -> None:
        session = _session(_at(MONDAY, 8, 0), _at(MONDAY, 15, 30))

        result = self.policy.evaluate(session)

        self.assertTrue(result.applicable)
        self.assertEqual(result.amount, Decimal("15.00"))

    def test_exit_just_before_1530_is_excluded(self) -> None:
        session = _session(_at(MONDAY, 8, 0), _at(MONDAY, 15, 29, 59))

        result = self.policy.evaluate(session)

        self.assertFalse(result.applicable)
        self.assertEqual(result.details["reason"], "exit_time_outside_window")

    def test_exit_exactly_at_1900_is_excluded(self) -> None:
        # 19:00 is the exclusive end of the exit window.
        session = _session(_at(MONDAY, 8, 0), _at(MONDAY, 19, 0))

        result = self.policy.evaluate(session)

        self.assertFalse(result.applicable)
        self.assertIsNone(result.amount)
        self.assertEqual(result.details["reason"], "exit_time_outside_window")

    def test_exit_just_before_1900_is_included(self) -> None:
        session = _session(_at(MONDAY, 8, 0), _at(MONDAY, 18, 59, 59))

        result = self.policy.evaluate(session)

        self.assertTrue(result.applicable)
        self.assertEqual(result.amount, Decimal("15.00"))

    def test_cross_midnight_stay_is_rejected_as_not_same_calendar_day(self) -> None:
        # Entry Monday 08:00, exit Tuesday 05:00 (21h, under the 24h cap):
        # the different-calendar-day rule rejects it before any clock-window
        # check. Note that an exit which is BOTH on the next day AND inside
        # the 15:30-19:00 window is impossible under 24h (the earliest such
        # exit is ~30.5h after the latest qualifying entry), so any
        # cross-midnight Early Bird stay is rejected by exactly one of
        # not_same_calendar_day / stay_longer_than_24_hours.
        session = _session(_at(MONDAY, 8, 0), _at(TUESDAY, 5, 0))

        result = self.policy.evaluate(session)

        self.assertFalse(result.applicable)
        self.assertIsNone(result.amount)
        self.assertEqual(result.details["reason"], "not_same_calendar_day")


class NightOwlWindowBoundaryTests(SimpleTestCase):
    """AC2: Night Owl entry window, next-consecutive-day exit window.

    Entry window 18:00 (inclusive) - 23:59:59 (inclusive, end of calendar
    day); exit window 05:00 (inclusive) - 10:00 (exclusive) on the next
    consecutive calendar day.
    """

    def setUp(self) -> None:
        self.policy = NightOwlPolicy()

    def test_entry_exactly_at_1800_is_included(self) -> None:
        session = _session(_at(MONDAY, 18, 0), _at(TUESDAY, 6, 0))

        result = self.policy.evaluate(session)

        self.assertTrue(result.applicable)
        self.assertEqual(result.amount, Decimal("8.00"))
        self.assertEqual(result.details["applicability_reason"], "applicable")

    def test_entry_at_1759_is_excluded(self) -> None:
        session = _session(_at(MONDAY, 17, 59), _at(TUESDAY, 6, 0))

        result = self.policy.evaluate(session)

        self.assertFalse(result.applicable)
        self.assertIsNone(result.amount)
        self.assertEqual(result.details["reason"], "entry_time_outside_window")

    def test_entry_exactly_at_2359_is_included(self) -> None:
        # The PRD allows entry up to 23:59:59 inclusive (end of calendar
        # day); the code models the window end as time.max, so 23:59:00 and
        # any later second of the day still qualify.
        session = _session(_at(MONDAY, 23, 59, 0), _at(TUESDAY, 6, 0))

        result = self.policy.evaluate(session)

        self.assertTrue(result.applicable)
        self.assertEqual(result.amount, Decimal("8.00"))

    def test_exit_exactly_at_0500_is_included(self) -> None:
        session = _session(_at(MONDAY, 20, 0), _at(TUESDAY, 5, 0))

        result = self.policy.evaluate(session)

        self.assertTrue(result.applicable)
        self.assertEqual(result.amount, Decimal("8.00"))

    def test_exit_just_before_0500_is_excluded(self) -> None:
        session = _session(_at(MONDAY, 20, 0), _at(TUESDAY, 4, 59, 59))

        result = self.policy.evaluate(session)

        self.assertFalse(result.applicable)
        self.assertEqual(result.details["reason"], "exit_time_outside_window")

    def test_exit_exactly_at_1000_is_excluded(self) -> None:
        # 10:00 is the exclusive end of the exit window.
        session = _session(_at(MONDAY, 20, 0), _at(TUESDAY, 10, 0))

        result = self.policy.evaluate(session)

        self.assertFalse(result.applicable)
        self.assertIsNone(result.amount)
        self.assertEqual(result.details["reason"], "exit_time_outside_window")

    def test_exit_just_before_1000_is_included(self) -> None:
        session = _session(_at(MONDAY, 20, 0), _at(TUESDAY, 9, 59, 59))

        result = self.policy.evaluate(session)

        self.assertTrue(result.applicable)
        self.assertEqual(result.amount, Decimal("8.00"))

    def test_same_day_exit_is_rejected_as_not_next_consecutive_day(self) -> None:
        session = _session(_at(MONDAY, 18, 0), _at(MONDAY, 23, 0))

        result = self.policy.evaluate(session)

        self.assertFalse(result.applicable)
        self.assertIsNone(result.amount)
        self.assertEqual(
            result.details["reason"],
            "not_next_consecutive_calendar_day",
        )

    def test_exit_two_days_later_is_rejected_by_the_24h_rule_first(self) -> None:
        # Entry Monday 18:00, exit Wednesday 05:00 (35h). A non-consecutive
        # next exit is necessarily longer than 24h, and the code checks the
        # 24h cap BEFORE the consecutive-day rule, so the documented reason
        # is stay_longer_than_24_hours (not
        # not_next_consecutive_calendar_day). This pins the actual code
        # semantics.
        session = _session(_at(MONDAY, 18, 0), _at(WEDNESDAY, 5, 0))

        result = self.policy.evaluate(session)

        self.assertFalse(result.applicable)
        self.assertIsNone(result.amount)
        self.assertEqual(result.details["reason"], "stay_longer_than_24_hours")


class SpecialLoyaltyDiscountTests(SimpleTestCase):
    """AC3: loyalty discounts applied to the flat base before the multiplier.

    The code computes ``base * (1 - discount) * vehicle_multiplier`` with a
    single final quantization, so the exact per-tier amounts below pin both
    the discount values and the order of operations.
    """

    def test_early_bird_loyalty_tiers_produce_exact_car_amounts(self) -> None:
        policy = EarlyBirdPolicy()
        cases = [
            (LoyaltyTier.NONE, "0", Decimal("15.00")),
            (LoyaltyTier.SILVER, "0.10", Decimal("13.50")),
            (LoyaltyTier.GOLD, "0.20", Decimal("12.00")),
            (LoyaltyTier.PLATINUM, "0.30", Decimal("10.50")),
        ]

        for loyalty_tier, expected_discount, expected_amount in cases:
            with self.subTest(loyalty_tier=loyalty_tier):
                session = _session(
                    _at(MONDAY, 8, 0),
                    _at(MONDAY, 16, 0),
                    loyalty_tier=loyalty_tier,
                )
                result = policy.evaluate(session)

                self.assertTrue(result.applicable)
                self.assertEqual(result.amount, expected_amount)
                # Discount is applied to the $15.00 flat base before the
                # vehicle multiplier (1.0 for a car here).
                self.assertEqual(result.details["base_amount"], "15.00")
                self.assertEqual(result.details["loyalty_tier"], loyalty_tier)
                self.assertEqual(result.details["loyalty_discount"], expected_discount)
                self.assertEqual(result.details["vehicle_multiplier"], "1.0")
                self.assertEqual(result.details["final_amount"], str(expected_amount))

    def test_night_owl_loyalty_tiers_produce_exact_car_amounts(self) -> None:
        policy = NightOwlPolicy()
        cases = [
            (LoyaltyTier.NONE, "0", Decimal("8.00")),
            (LoyaltyTier.SILVER, "0.10", Decimal("7.20")),
            (LoyaltyTier.GOLD, "0.20", Decimal("6.40")),
            (LoyaltyTier.PLATINUM, "0.30", Decimal("5.60")),
        ]

        for loyalty_tier, expected_discount, expected_amount in cases:
            with self.subTest(loyalty_tier=loyalty_tier):
                session = _session(
                    _at(MONDAY, 20, 0),
                    _at(TUESDAY, 8, 0),
                    loyalty_tier=loyalty_tier,
                )
                result = policy.evaluate(session)

                self.assertTrue(result.applicable)
                self.assertEqual(result.amount, expected_amount)
                self.assertEqual(result.details["base_amount"], "8.00")
                self.assertEqual(result.details["loyalty_tier"], loyalty_tier)
                self.assertEqual(result.details["loyalty_discount"], expected_discount)
                self.assertEqual(result.details["vehicle_multiplier"], "1.0")
                self.assertEqual(result.details["final_amount"], str(expected_amount))


class SpecialVehicleMultiplierTests(SimpleTestCase):
    """AC4: vehicle multipliers (0.8 / 1.0 / 2.0) under flat-rate specials."""

    def test_night_owl_vehicle_multipliers_with_no_loyalty(self) -> None:
        # PRD values: Night Owl car $8.00, motorcycle 0.8x, bus 2.0x.
        policy = NightOwlPolicy()
        cases = [
            (VehicleType.MOTORCYCLE, "0.8", Decimal("6.40")),
            (VehicleType.CAR, "1.0", Decimal("8.00")),
            (VehicleType.BUS, "2.0", Decimal("16.00")),
        ]

        for vehicle_type, expected_multiplier, expected_amount in cases:
            with self.subTest(vehicle_type=vehicle_type):
                session = _session(
                    _at(MONDAY, 20, 0),
                    _at(TUESDAY, 8, 0),
                    vehicle_type=vehicle_type,
                )
                result = policy.evaluate(session)

                self.assertTrue(result.applicable)
                self.assertEqual(result.amount, expected_amount)
                self.assertEqual(result.details["vehicle_type"], vehicle_type)
                self.assertEqual(result.details["vehicle_multiplier"], expected_multiplier)
                self.assertEqual(result.details["loyalty_discount"], "0")
                self.assertEqual(result.details["final_amount"], str(expected_amount))

    def test_early_bird_vehicle_multipliers_with_no_loyalty(self) -> None:
        # Early Bird car $15.00: motorcycle $12.00, car $15.00, bus $30.00.
        policy = EarlyBirdPolicy()
        cases = [
            (VehicleType.MOTORCYCLE, "0.8", Decimal("12.00")),
            (VehicleType.CAR, "1.0", Decimal("15.00")),
            (VehicleType.BUS, "2.0", Decimal("30.00")),
        ]

        for vehicle_type, expected_multiplier, expected_amount in cases:
            with self.subTest(vehicle_type=vehicle_type):
                session = _session(
                    _at(MONDAY, 8, 0),
                    _at(MONDAY, 16, 0),
                    vehicle_type=vehicle_type,
                )
                result = policy.evaluate(session)

                self.assertTrue(result.applicable)
                self.assertEqual(result.amount, expected_amount)
                self.assertEqual(result.details["vehicle_multiplier"], expected_multiplier)
                self.assertEqual(result.details["final_amount"], str(expected_amount))

    def test_combined_loyalty_and_vehicle_math_is_exact(self) -> None:
        # Discount first on the flat base, then the vehicle multiplier:
        #   Night Owl motorcycle GOLD:    8.00 * (1 - 0.20) * 0.8 = 5.12
        #   Early Bird bus PLATINUM:     15.00 * (1 - 0.30) * 2.0 = 21.00
        #   Night Owl car SILVER:        8.00 * (1 - 0.10) * 1.0 = 7.20
        cases = [
            (
                NightOwlPolicy(),
                _session(
                    _at(MONDAY, 20, 0),
                    _at(TUESDAY, 8, 0),
                    vehicle_type=VehicleType.MOTORCYCLE,
                    loyalty_tier=LoyaltyTier.GOLD,
                ),
                Decimal("5.12"),
                "Night Owl motorcycle gold",
            ),
            (
                EarlyBirdPolicy(),
                _session(
                    _at(MONDAY, 8, 0),
                    _at(MONDAY, 16, 0),
                    vehicle_type=VehicleType.BUS,
                    loyalty_tier=LoyaltyTier.PLATINUM,
                ),
                Decimal("21.00"),
                "Early Bird bus platinum",
            ),
            (
                NightOwlPolicy(),
                _session(
                    _at(MONDAY, 20, 0),
                    _at(TUESDAY, 8, 0),
                    vehicle_type=VehicleType.CAR,
                    loyalty_tier=LoyaltyTier.SILVER,
                ),
                Decimal("7.20"),
                "Night Owl car silver",
            ),
        ]

        for policy, session, expected_amount, label in cases:
            with self.subTest(label=label):
                result = policy.evaluate(session)
                self.assertTrue(result.applicable)
                self.assertEqual(result.amount, expected_amount)
                self.assertEqual(result.details["final_amount"], str(expected_amount))


class SpecialTwentyFourHourLimitTests(SimpleTestCase):
    """AC5: stays longer than 24 hours invalidate both specials.

    Documented code semantics: the 24h cap is checked BEFORE the window
    rules, but the windows themselves bound any qualifying stay to far less
    than 24h (Early Bird max ~12h59m same-day; Night Owl max ~15h59m
    overnight). Therefore:
    - a stay of EXACTLY 24h passes the 24h check (it is not "longer than")
      but is always rejected by the day/window rules -- never by the 24h
      rule;
    - a stay of 24h + 1s is rejected with ``stay_longer_than_24_hours``
      before any window check runs.
    """

    def test_exactly_24h_early_bird_is_rejected_by_the_day_rule_not_the_24h_rule(self) -> None:
        # Monday 06:00 -> Tuesday 06:00 is exactly 24h. It is not "longer
        # than 24h", so the 24h rule does not fire; the same-calendar-day
        # rule rejects it instead.
        session = _session(_at(MONDAY, 6, 0), _at(TUESDAY, 6, 0))

        result = EarlyBirdPolicy().evaluate(session)

        self.assertFalse(result.applicable)
        self.assertIsNone(result.amount)
        self.assertEqual(result.details["reason"], "not_same_calendar_day")

    def test_exactly_24h_night_owl_is_rejected_by_the_exit_window_rule(self) -> None:
        # Monday 18:00 -> Tuesday 18:00 is exactly 24h on the next
        # consecutive day, but the 18:00 exit is outside the 05:00-10:00
        # exit window, so the window rule (not the 24h rule) rejects it.
        session = _session(_at(MONDAY, 18, 0), _at(TUESDAY, 18, 0))

        result = NightOwlPolicy().evaluate(session)

        self.assertFalse(result.applicable)
        self.assertIsNone(result.amount)
        self.assertEqual(result.details["reason"], "exit_time_outside_window")

    def test_24h_plus_1s_invalidates_early_bird_with_the_24h_reason(self) -> None:
        session = _session(_at(MONDAY, 6, 0), _at(TUESDAY, 6, 0, 1))

        result = EarlyBirdPolicy().evaluate(session)

        self.assertFalse(result.applicable)
        self.assertIsNone(result.amount)
        self.assertEqual(result.details["reason"], "stay_longer_than_24_hours")

    def test_24h_plus_1s_invalidates_night_owl_with_the_24h_reason(self) -> None:
        session = _session(_at(MONDAY, 18, 0), _at(TUESDAY, 18, 0, 1))

        result = NightOwlPolicy().evaluate(session)

        self.assertFalse(result.applicable)
        self.assertIsNone(result.amount)
        self.assertEqual(result.details["reason"], "stay_longer_than_24_hours")


class SpecialBestValueSelectionTests(TestCase):
    """AC6: best-value selection with persisted RateEvaluation audit rows.

    With the REAL policy parameters, a standard hourly charge can never be
    cheaper than an applicable special: the special windows force a minimum
    stay of ~6.5h (Early Bird: latest entry 08:59:59, earliest exit 15:30)
    or ~5h (Night Owl: latest entry 23:59:59, earliest exit 05:00), and the
    standard rate for any such stay (>= $16.00 car off-peak) always exceeds
    the discounted flat special (<= $15.00 / $8.00 car). So the
    standard-wins and exact-tie branches of the calculator are exercised
    here with stub policies on real DB-backed sessions; the special-wins
    cases use the real default calculator.
    """

    def setUp(self) -> None:
        self.spot = ParkingSpot.objects.create(
            level=1,
            number="SPCV-01",
            spot_type=SpotType.COMPACT,
        )
        self.registration_counter = 0

    def create_session(
        self,
        entered_at: datetime,
        exited_at: datetime,
        loyalty_tier: str = LoyaltyTier.NONE,
        vehicle_type: str = VehicleType.CAR,
    ) -> ParkingSession:
        self.registration_counter += 1
        vehicle = Vehicle.objects.create(
            registration=f"SPCV-{self.registration_counter:03d}",
            vehicle_type=vehicle_type,
        )
        return ParkingSession.objects.create(
            vehicle=vehicle,
            spot=self.spot,
            entered_at=entered_at,
            exited_at=exited_at,
            status=SessionStatus.CLOSED,
            loyalty_tier_snapshot=loyalty_tier,
        )

    def test_early_bird_special_wins_and_all_evaluations_are_persisted(self) -> None:
        # Monday 06:00 -> 16:00, car, no loyalty:
        #   Standard: 5.00 + 4.50 + 3.00 + 3.00 + 2.00*6 = 27.50
        #   Early Bird: 15.00 (flat, no discount)  -> cheapest, selected
        #   Night Owl: not applicable (same-day exit)
        session = self.create_session(
            _at(MONDAY, 6, 0),
            _at(MONDAY, 16, 0),
        )

        selected = ParkingRateCalculator().calculate(session)

        session.refresh_from_db()
        evaluations = {
            evaluation.policy: evaluation
            for evaluation in RateEvaluation.objects.filter(session=session)
        }
        self.assertEqual(
            set(evaluations),
            {RatePolicy.STANDARD, RatePolicy.EARLY_BIRD, RatePolicy.NIGHT_OWL},
        )
        self.assertEqual(evaluations[RatePolicy.STANDARD].amount, Decimal("27.50"))
        self.assertTrue(evaluations[RatePolicy.STANDARD].applicable)
        self.assertEqual(evaluations[RatePolicy.EARLY_BIRD].amount, Decimal("15.00"))
        self.assertEqual(
            evaluations[RatePolicy.EARLY_BIRD].details["loyalty_discount"],
            "0",
        )
        self.assertEqual(
            evaluations[RatePolicy.EARLY_BIRD].details["vehicle_multiplier"],
            "1.0",
        )
        self.assertFalse(evaluations[RatePolicy.NIGHT_OWL].applicable)
        self.assertIsNone(evaluations[RatePolicy.NIGHT_OWL].amount)
        self.assertEqual(
            evaluations[RatePolicy.NIGHT_OWL].details["reason"],
            "not_next_consecutive_calendar_day",
        )
        # Best value persisted on the session.
        self.assertEqual(selected.policy, RatePolicy.EARLY_BIRD)
        self.assertEqual(selected.amount, Decimal("15.00"))
        self.assertEqual(session.selected_evaluation, selected)
        self.assertEqual(session.charged_amount, Decimal("15.00"))

    def test_night_owl_special_wins_with_loyalty_discount_persisted(self) -> None:
        # Monday 20:00 -> Tuesday 08:00, car, platinum:
        #   Standard: 5.00 + 3.00 + 2.00*9 + 3.00 (peak 07:00-08:00) = 29.00
        #   Night Owl: 8.00 * (1 - 0.30) = 5.60  -> cheapest, selected
        session = self.create_session(
            _at(MONDAY, 20, 0),
            _at(TUESDAY, 8, 0),
            loyalty_tier=LoyaltyTier.PLATINUM,
        )

        selected = ParkingRateCalculator().calculate(session)

        session.refresh_from_db()
        evaluations = {
            evaluation.policy: evaluation
            for evaluation in RateEvaluation.objects.filter(session=session)
        }
        self.assertEqual(evaluations[RatePolicy.STANDARD].amount, Decimal("29.00"))
        self.assertEqual(evaluations[RatePolicy.NIGHT_OWL].amount, Decimal("5.60"))
        self.assertEqual(
            evaluations[RatePolicy.NIGHT_OWL].details["loyalty_discount"],
            "0.30",
        )
        self.assertFalse(evaluations[RatePolicy.EARLY_BIRD].applicable)
        self.assertEqual(selected.policy, RatePolicy.NIGHT_OWL)
        self.assertEqual(selected.amount, Decimal("5.60"))
        self.assertEqual(session.selected_evaluation, selected)
        self.assertEqual(session.charged_amount, Decimal("5.60"))

    def test_standard_wins_when_its_amount_is_lower(self) -> None:
        # Standard-wins branch: stub policies on a real DB-backed session
        # (see class docstring for why the real parameters cannot produce
        # this branch). Standard $10.00 < Early Bird $15.00 -> standard
        # selected and persisted.
        session = self.create_session(
            _at(MONDAY, 6, 0),
            _at(MONDAY, 16, 0),
        )
        calculator = ParkingRateCalculator(
            policies=[
                self.FixedPolicy(RatePolicy.STANDARD, Decimal("10.00")),
                self.FixedPolicy(RatePolicy.EARLY_BIRD, Decimal("15.00")),
                self.FixedPolicy(RatePolicy.NIGHT_OWL, None, applicable=False),
            ]
        )

        selected = calculator.calculate(session)

        session.refresh_from_db()
        self.assertEqual(selected.policy, RatePolicy.STANDARD)
        self.assertEqual(selected.amount, Decimal("10.00"))
        self.assertEqual(session.selected_evaluation, selected)
        self.assertEqual(session.charged_amount, Decimal("10.00"))
        self.assertEqual(RateEvaluation.objects.filter(session=session).count(), 3)

    def test_exact_tie_breaks_by_policy_order_standard_first(self) -> None:
        # All three policies produce the same amount: the tie must break by
        # configured policy order (standard, early_bird, night_owl), so
        # standard wins.
        session = self.create_session(
            _at(MONDAY, 6, 0),
            _at(MONDAY, 16, 0),
        )
        calculator = ParkingRateCalculator(
            policies=[
                self.FixedPolicy(RatePolicy.STANDARD, Decimal("12.00")),
                self.FixedPolicy(RatePolicy.EARLY_BIRD, Decimal("12.00")),
                self.FixedPolicy(RatePolicy.NIGHT_OWL, Decimal("12.00")),
            ]
        )

        selected = calculator.calculate(session)

        session.refresh_from_db()
        self.assertEqual(selected.policy, RatePolicy.STANDARD)
        self.assertEqual(selected.amount, Decimal("12.00"))
        self.assertEqual(session.charged_amount, Decimal("12.00"))

    def test_exact_tie_between_specials_breaks_toward_early_bird(self) -> None:
        # Without standard in the mix, an early_bird/night_owl tie breaks
        # toward early_bird (second in the default policy order).
        session = self.create_session(
            _at(MONDAY, 20, 0),
            _at(TUESDAY, 8, 0),
        )
        calculator = ParkingRateCalculator(
            policies=[
                self.FixedPolicy(RatePolicy.EARLY_BIRD, Decimal("12.00")),
                self.FixedPolicy(RatePolicy.NIGHT_OWL, Decimal("12.00")),
            ]
        )

        selected = calculator.calculate(session)

        session.refresh_from_db()
        self.assertEqual(selected.policy, RatePolicy.EARLY_BIRD)
        self.assertEqual(selected.amount, Decimal("12.00"))
        self.assertEqual(session.charged_amount, Decimal("12.00"))

    class FixedPolicy:
        """Stub policy returning a fixed amount; used to reach selection
        branches the real rate parameters cannot produce."""

        def __init__(
            self,
            policy: str,
            amount: Decimal | None,
            applicable: bool = True,
        ) -> None:
            self.policy = policy
            self.amount = amount
            self.applicable = applicable

        def evaluate(self, session) -> PolicyResult:
            return PolicyResult(
                policy=self.policy,
                applicable=self.applicable,
                amount=self.amount if self.applicable else None,
                details={
                    "reason": "stub_policy",
                    "quoted_amount": self.amount,
                },
            )
