"""Dedicated scenario tests for the Standard Hourly pricing policy (TASK-5.1).

These tests fill the gaps left by ``StandardHourlyPolicyTests`` in ``tests.py``
and pin each acceptance criterion of TASK-5.1 with a clearly-named test.

Conventions:
- Sessions are lightweight ``SimpleNamespace`` objects exposing only the
  attributes ``StandardHourlyPolicy.evaluate`` reads (``entered_at``,
  ``exited_at``, ``vehicle.vehicle_type``).
- Tests still subclass ``TestCase`` because the policy queries the
  ``PublicHoliday`` table on every evaluation, so a database connection is
  required even for non-holiday scenarios.
- Datetimes are timezone-aware UTC, matching the rest of the suite.
- Fixed ISO dates with explicit weekday comments:
    2026-09-28 -> Monday (weekday, no holiday)
    2026-09-29 -> Tuesday (weekday, no holiday)
    2026-10-03 -> Saturday (weekend)
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

from django.test import TestCase

from parking.models import PublicHoliday, RatePolicy, VehicleType
from parking.pricing import (
    PEAK_MULTIPLIER,
    StandardHourlyPolicy,
)

# 2026-09-28 is a Monday (verified weekday; used for peak/holiday scenarios).
MONDAY = date(2026, 9, 28)
# 2026-09-29 is a Tuesday (verified weekday; used for plain weekday scenarios).
TUESDAY = date(2026, 9, 29)
# 2026-10-03 is a Saturday (verified weekend; used for off-peak scenarios).
SATURDAY = date(2026, 10, 3)


def _at(day: date, hour: int, minute: int = 0, second: int = 0) -> datetime:
    """Build a timezone-aware UTC datetime on the given day."""

    return datetime(day.year, day.month, day.day, hour, minute, second, tzinfo=timezone.utc)


def _session(
    entered_at: datetime,
    exited_at: datetime,
    vehicle_type: str = VehicleType.CAR,
) -> SimpleNamespace:
    """Build a lightweight session object for direct policy evaluation."""

    return SimpleNamespace(
        entered_at=entered_at,
        exited_at=exited_at,
        vehicle=SimpleNamespace(vehicle_type=vehicle_type),
    )


class StandardHourlyRoundingTests(TestCase):
    """AC1: duration is rounded upward to full hours, without over-rounding."""

    def setUp(self) -> None:
        self.policy = StandardHourlyPolicy()

    def test_partial_duration_rounds_up_to_next_full_hour(self) -> None:
        # 1h01m on a Saturday (no peak): must bill 2 hourly blocks.
        session = _session(_at(SATURDAY, 11, 0), _at(SATURDAY, 12, 1))

        result = self.policy.evaluate(session)

        self.assertTrue(result.applicable)
        self.assertEqual(result.details["rounded_hours"], 2)
        self.assertEqual(len(result.details["hours"]), 2)
        # 2 blocks off-peak: first hour 5.00 + second hour 3.00.
        self.assertEqual(result.amount, Decimal("8.00"))

    def test_one_second_over_a_hour_still_rounds_up(self) -> None:
        # 1h00m01s must be billed as 2 blocks, not 1.
        session = _session(_at(SATURDAY, 11, 0, 0), _at(SATURDAY, 12, 0, 1))

        result = self.policy.evaluate(session)

        self.assertEqual(result.details["rounded_hours"], 2)
        self.assertEqual(len(result.details["hours"]), 2)
        self.assertEqual(result.amount, Decimal("8.00"))

    def test_exact_whole_hours_do_not_over_round(self) -> None:
        # Exactly 2h00m00s must bill exactly 2 blocks (not 3).
        session = _session(_at(SATURDAY, 11, 0), _at(SATURDAY, 13, 0))

        result = self.policy.evaluate(session)

        self.assertEqual(result.details["rounded_hours"], 2)
        self.assertEqual(len(result.details["hours"]), 2)
        self.assertEqual(result.amount, Decimal("8.00"))

    def test_just_under_two_hours_rounds_up_to_two(self) -> None:
        # 1h59m59s must bill exactly 2 blocks (not 3).
        session = _session(_at(SATURDAY, 11, 0), _at(SATURDAY, 12, 59, 59))

        result = self.policy.evaluate(session)

        self.assertEqual(result.details["rounded_hours"], 2)
        self.assertEqual(len(result.details["hours"]), 2)
        self.assertEqual(result.amount, Decimal("8.00"))


class StandardHourlyBaseRateTests(TestCase):
    """AC2: first-hour $5.00, second-hour $3.00, subsequent-hour $2.00."""

    def setUp(self) -> None:
        self.policy = StandardHourlyPolicy()

    def test_first_hour_charges_five_dollars_off_peak(self) -> None:
        session = _session(_at(SATURDAY, 11, 0), _at(SATURDAY, 12, 0))

        result = self.policy.evaluate(session)

        self.assertEqual(result.amount, Decimal("5.00"))
        self.assertEqual(result.details["hours"][0]["base_rate"], "5.00")
        self.assertEqual(result.details["hours"][0]["amount"], "5.00")

    def test_second_hour_charges_three_dollars_off_peak(self) -> None:
        session = _session(_at(SATURDAY, 11, 0), _at(SATURDAY, 13, 0))

        result = self.policy.evaluate(session)

        self.assertEqual(result.details["hours"][1]["base_rate"], "3.00")
        self.assertEqual(result.details["hours"][1]["amount"], "3.00")
        self.assertEqual(result.amount, Decimal("8.00"))

    def test_subsequent_hours_charge_two_dollars_each_off_peak(self) -> None:
        # 3-hour Saturday stay: 5.00 + 3.00 + 2.00 = 10.00.
        session = _session(_at(SATURDAY, 11, 0), _at(SATURDAY, 14, 0))

        result = self.policy.evaluate(session)

        self.assertEqual(
            [hour["base_rate"] for hour in result.details["hours"]],
            ["5.00", "3.00", "2.00"],
        )
        self.assertEqual(
            [hour["amount"] for hour in result.details["hours"]],
            ["5.00", "3.00", "2.00"],
        )
        self.assertEqual(result.amount, Decimal("10.00"))

    def test_multi_hour_stay_hits_all_three_rate_tiers(self) -> None:
        # 5-hour Saturday stay (11:00-16:00, all off-peak; the 15:00-16:00
        # block ends exactly at the 16:00 exclusive peak start):
        # 5.00 + 3.00 + 2.00 + 2.00 + 2.00 = 14.00.
        session = _session(_at(SATURDAY, 11, 0), _at(SATURDAY, 16, 0))

        result = self.policy.evaluate(session)

        self.assertEqual(result.details["rounded_hours"], 5)
        self.assertEqual(
            [hour["amount"] for hour in result.details["hours"]],
            ["5.00", "3.00", "2.00", "2.00", "2.00"],
        )
        self.assertFalse(any(hour["peak"] for hour in result.details["hours"]))
        self.assertEqual(result.amount, Decimal("14.00"))


class StandardHourlyFloatingBlockTests(TestCase):
    """AC3: hourly blocks float from the entry timestamp, not clock hours."""

    def setUp(self) -> None:
        self.policy = StandardHourlyPolicy()

    def test_block_boundaries_are_entry_plus_n_hours_not_clock_aligned(self) -> None:
        # Monday 08:45 -> 11:15 (2h30m, rounds to 3 blocks).
        # Blocks must be 08:45-09:45, 09:45-10:45, 10:45-11:45 --
        # NOT aligned to 09:00, 10:00, 11:00.
        session = _session(_at(MONDAY, 8, 45), _at(MONDAY, 11, 15))

        result = self.policy.evaluate(session)

        self.assertEqual(result.details["rounded_hours"], 3)
        self.assertEqual(
            [(hour["start"], hour["end"]) for hour in result.details["hours"]],
            [
                ("2026-09-28T08:45:00+00:00", "2026-09-28T09:45:00+00:00"),
                ("2026-09-28T09:45:00+00:00", "2026-09-28T10:45:00+00:00"),
                ("2026-09-28T10:45:00+00:00", "2026-09-28T11:45:00+00:00"),
            ],
        )
        # Block 1 (08:45-09:45) and block 2 (09:45-10:45) overlap the 7-10
        # AM peak; block 3 (10:45-11:45) does not.
        self.assertEqual(
            [hour["peak"] for hour in result.details["hours"]],
            [True, True, False],
        )
        self.assertEqual(
            [hour["amount"] for hour in result.details["hours"]],
            ["7.50", "4.50", "2.00"],
        )
        self.assertEqual(result.amount, Decimal("14.00"))

    def test_prd_floating_example_entry_at_half_past(self) -> None:
        # PRD worked example: weekday entry 06:30, exit 08:30 (2 hours).
        # Hour 1 (06:30-07:30) is $7.50, hour 2 (07:30-08:30) is $4.50.
        session = _session(_at(MONDAY, 6, 30), _at(MONDAY, 8, 30))

        result = self.policy.evaluate(session)

        self.assertEqual(result.policy, RatePolicy.STANDARD)
        self.assertEqual(
            [(hour["start"], hour["end"]) for hour in result.details["hours"]],
            [
                ("2026-09-28T06:30:00+00:00", "2026-09-28T07:30:00+00:00"),
                ("2026-09-28T07:30:00+00:00", "2026-09-28T08:30:00+00:00"),
            ],
        )
        self.assertEqual(
            [hour["amount"] for hour in result.details["hours"]],
            ["7.50", "4.50"],
        )
        self.assertEqual(result.amount, Decimal("12.00"))


class StandardHourlyPartialPeakOverlapTests(TestCase):
    """AC4: any partial peak overlap charges the WHOLE block at 1.5x."""

    def setUp(self) -> None:
        self.policy = StandardHourlyPolicy()

    def test_block_ending_inside_peak_is_charged_fully_at_peak_rate(self) -> None:
        # Block 09:30-10:30 overlaps the 7:00-10:00 peak only for 09:30-10:00,
        # so the entire first-hour block is charged $5.00 * 1.5 = $7.50.
        session = _session(_at(MONDAY, 9, 30), _at(MONDAY, 10, 30))

        result = self.policy.evaluate(session)

        self.assertEqual(result.details["rounded_hours"], 1)
        block = result.details["hours"][0]
        self.assertTrue(block["peak"])
        self.assertEqual(block["peak_multiplier"], str(PEAK_MULTIPLIER))
        # Combined multiplier is 1.0 * 1.5; Decimal multiplication keeps the
        # operand precision, so it serialises as "1.50".
        self.assertEqual(block["multiplier"], "1.50")
        self.assertEqual(block["amount"], "7.50")
        self.assertEqual(result.amount, Decimal("7.50"))

    def test_block_starting_inside_peak_is_charged_fully_at_peak_rate(self) -> None:
        # Block 06:30-07:30 overlaps the peak only for 07:00-07:30, yet the
        # whole block is charged $5.00 * 1.5 = $7.50.
        session = _session(_at(MONDAY, 6, 30), _at(MONDAY, 7, 30))

        result = self.policy.evaluate(session)

        block = result.details["hours"][0]
        self.assertTrue(block["peak"])
        self.assertEqual(block["amount"], "7.50")
        self.assertEqual(result.amount, Decimal("7.50"))

    def test_second_hour_block_partially_in_peak_uses_second_hour_rate(self) -> None:
        # Monday 09:00 -> 11:00: block 2 is 10:00-11:00 (fully off-peak) but
        # block 1 is 09:00-10:00 (fully in peak). Total: 7.50 + 3.00 = 10.50.
        session = _session(_at(MONDAY, 9, 0), _at(MONDAY, 11, 0))

        result = self.policy.evaluate(session)

        self.assertEqual(
            [(hour["peak"], hour["amount"]) for hour in result.details["hours"]],
            [(True, "7.50"), (False, "3.00")],
        )
        self.assertEqual(result.amount, Decimal("10.50"))


class StandardHourlyPeakBoundaryTests(TestCase):
    """AC5: peak window starts are inclusive, ends are exclusive."""

    def setUp(self) -> None:
        self.policy = StandardHourlyPolicy()

    def test_block_ending_exactly_at_10am_is_peak(self) -> None:
        # 09:00-10:00 ends exactly at the exclusive 10:00 boundary: still peak.
        session = _session(_at(MONDAY, 9, 0), _at(MONDAY, 10, 0))

        result = self.policy.evaluate(session)

        self.assertTrue(result.details["hours"][0]["peak"])
        self.assertEqual(result.amount, Decimal("7.50"))

    def test_block_starting_exactly_at_10am_is_not_peak(self) -> None:
        # 10:00-11:00 starts exactly at the exclusive 10:00 boundary: no peak.
        session = _session(_at(MONDAY, 10, 0), _at(MONDAY, 11, 0))

        result = self.policy.evaluate(session)

        self.assertFalse(result.details["hours"][0]["peak"])
        self.assertEqual(result.amount, Decimal("5.00"))

    def test_block_starting_exactly_at_7am_is_peak(self) -> None:
        # 07:00-08:00 starts exactly at the inclusive 07:00 boundary: peak.
        session = _session(_at(MONDAY, 7, 0), _at(MONDAY, 8, 0))

        result = self.policy.evaluate(session)

        self.assertTrue(result.details["hours"][0]["peak"])
        self.assertEqual(result.amount, Decimal("7.50"))

    def test_block_ending_exactly_before_7am_is_not_peak(self) -> None:
        # 06:00-07:00 ends exactly at the inclusive 07:00 boundary: no peak.
        session = _session(_at(MONDAY, 6, 0), _at(MONDAY, 7, 0))

        result = self.policy.evaluate(session)

        self.assertFalse(result.details["hours"][0]["peak"])
        self.assertEqual(result.amount, Decimal("5.00"))

    def test_evening_peak_boundaries_use_inclusive_start_exclusive_end(self) -> None:
        cases = [
            # (entry, exit, expected_peak, expected_amount, label)
            (_at(MONDAY, 16, 0), _at(MONDAY, 17, 0), True, Decimal("7.50"),
             "block starting exactly at 16:00 is peak"),
            (_at(MONDAY, 18, 0), _at(MONDAY, 19, 0), True, Decimal("7.50"),
             "block ending exactly at 19:00 is peak"),
            (_at(MONDAY, 19, 0), _at(MONDAY, 20, 0), False, Decimal("5.00"),
             "block starting exactly at 19:00 is not peak"),
            (_at(MONDAY, 15, 0), _at(MONDAY, 16, 0), False, Decimal("5.00"),
             "block ending exactly at 16:00 is not peak"),
        ]

        for entered_at, exited_at, expected_peak, expected_amount, label in cases:
            with self.subTest(label=label):
                result = self.policy.evaluate(_session(entered_at, exited_at))
                self.assertEqual(
                    result.details["hours"][0]["peak"],
                    expected_peak,
                )
                self.assertEqual(result.amount, expected_amount)


class StandardHourlyPeakDayRulesTests(TestCase):
    """AC6: peaks apply only on weekdays that are not public holidays."""

    def setUp(self) -> None:
        self.policy = StandardHourlyPolicy()

    def test_public_holiday_disables_weekday_peak_surcharge(self) -> None:
        # 2026-09-28 is a Monday; marking it a public holiday must remove the
        # 1.5x peak surcharge for the same weekday time window.
        PublicHoliday.objects.create(date=MONDAY, name="Observed Holiday")
        session = _session(_at(MONDAY, 7, 0), _at(MONDAY, 8, 0))

        result = self.policy.evaluate(session)

        self.assertTrue(result.applicable)
        self.assertFalse(result.details["hours"][0]["peak"])
        self.assertEqual(result.details["hours"][0]["peak_multiplier"], "1.0")
        self.assertEqual(result.amount, Decimal("5.00"))

    def test_same_weekday_time_is_peak_without_holiday_and_flat_with_holiday(self) -> None:
        # Control: the identical Monday 07:00-08:00 stay is peak on a normal
        # weekday (Tuesday) and flat on the holiday Monday.
        weekday_result = self.policy.evaluate(
            _session(_at(TUESDAY, 7, 0), _at(TUESDAY, 8, 0)),
        )
        PublicHoliday.objects.create(date=MONDAY, name="Observed Holiday")
        holiday_result = self.policy.evaluate(
            _session(_at(MONDAY, 7, 0), _at(MONDAY, 8, 0)),
        )

        self.assertTrue(weekday_result.details["hours"][0]["peak"])
        self.assertEqual(weekday_result.amount, Decimal("7.50"))
        self.assertFalse(holiday_result.details["hours"][0]["peak"])
        self.assertEqual(holiday_result.amount, Decimal("5.00"))

    def test_weekend_blocks_in_peak_windows_are_not_peak(self) -> None:
        # Saturday stays inside both peak windows must be charged flat.
        morning = self.policy.evaluate(
            _session(_at(SATURDAY, 7, 0), _at(SATURDAY, 8, 0)),
        )
        evening = self.policy.evaluate(
            _session(_at(SATURDAY, 16, 0), _at(SATURDAY, 17, 0)),
        )

        self.assertFalse(morning.details["hours"][0]["peak"])
        self.assertEqual(morning.amount, Decimal("5.00"))
        self.assertFalse(evening.details["hours"][0]["peak"])
        self.assertEqual(evening.amount, Decimal("5.00"))


class StandardHourlyVehicleMultiplierTests(TestCase):
    """AC7: vehicle multipliers (0.8 / 1.0 / 2.0) apply per hourly block."""

    def setUp(self) -> None:
        self.policy = StandardHourlyPolicy()

    def test_first_hour_off_peak_amounts_by_vehicle_type(self) -> None:
        # Saturday 11:00-12:00 (off-peak), first hour:
        # motorcycle 5.00 * 0.8 = 4.00, car 5.00 * 1.0 = 5.00, bus 5.00 * 2.0 = 10.00.
        cases = [
            (VehicleType.MOTORCYCLE, "0.8", Decimal("4.00")),
            (VehicleType.CAR, "1.0", Decimal("5.00")),
            (VehicleType.BUS, "2.0", Decimal("10.00")),
        ]

        for vehicle_type, expected_multiplier, expected_amount in cases:
            with self.subTest(vehicle_type=vehicle_type):
                result = self.policy.evaluate(
                    _session(
                        _at(SATURDAY, 11, 0),
                        _at(SATURDAY, 12, 0),
                        vehicle_type=vehicle_type,
                    ),
                )
                block = result.details["hours"][0]
                self.assertEqual(block["vehicle_multiplier"], expected_multiplier)
                # Combined multiplier is vehicle * 1.0 (off-peak); Decimal
                # multiplication keeps operand precision, e.g. "0.80".
                self.assertEqual(block["multiplier"], expected_multiplier + "0")
                self.assertEqual(block["amount"], str(expected_amount))
                self.assertEqual(result.amount, expected_amount)

    def test_vehicle_multiplier_applies_to_every_block_of_a_multi_hour_stay(self) -> None:
        # Bus, Saturday 11:00-14:00 (off-peak): each block doubled:
        # 10.00 + 6.00 + 4.00 = 20.00.
        session = _session(
            _at(SATURDAY, 11, 0),
            _at(SATURDAY, 14, 0),
            vehicle_type=VehicleType.BUS,
        )

        result = self.policy.evaluate(session)

        self.assertEqual(
            [hour["amount"] for hour in result.details["hours"]],
            ["10.00", "6.00", "4.00"],
        )
        self.assertEqual(result.amount, Decimal("20.00"))

    def test_vehicle_and_peak_multipliers_combine_per_block(self) -> None:
        # Motorcycle, Monday 07:00-08:00 (peak): 5.00 * 0.8 * 1.5 = 6.00.
        session = _session(
            _at(MONDAY, 7, 0),
            _at(MONDAY, 8, 0),
            vehicle_type=VehicleType.MOTORCYCLE,
        )

        result = self.policy.evaluate(session)

        block = result.details["hours"][0]
        self.assertTrue(block["peak"])
        self.assertEqual(block["peak_multiplier"], str(PEAK_MULTIPLIER))
        self.assertEqual(block["multiplier"], "1.20")
        self.assertEqual(block["amount"], "6.00")
        self.assertEqual(result.amount, Decimal("6.00"))
