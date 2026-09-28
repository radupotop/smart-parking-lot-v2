"""Tests for the parking app."""

from datetime import date, datetime, time, timezone
from decimal import Decimal

from django.contrib import admin as django_admin
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from parking.admin import RateEvaluationInline
from parking.models import (
    Customer,
    LoyaltyTier,
    ParkingSession,
    ParkingSpot,
    PublicHoliday,
    RateEvaluation,
    RatePolicy,
    SessionStatus,
    SpotType,
    SpotTypeVehicleCompatibility,
    Vehicle,
    VehicleType,
)
from parking.pricing import (
    EARLY_BIRD_ENTRY_WINDOW,
    EARLY_BIRD_EXIT_WINDOW,
    EARLY_BIRD_RATE,
    LOYALTY_DISCOUNTS,
    NIGHT_OWL_ENTRY_WINDOW,
    NIGHT_OWL_EXIT_WINDOW,
    NIGHT_OWL_RATE,
    PEAK_MULTIPLIER,
    PEAK_WINDOWS,
    STANDARD_FIRST_HOUR_RATE,
    STANDARD_HOURLY_BASE_RATES,
    STANDARD_SECOND_HOUR_RATE,
    STANDARD_SUBSEQUENT_HOUR_RATE,
    StandardHourlyPolicy,
    TimeWindow,
    VEHICLE_MULTIPLIERS,
    contains_time,
    interval_overlaps,
    is_weekday_excluding_public_holidays,
    quantize_currency,
    window_for_date,
)


class ProjectConfigurationTests(SimpleTestCase):
    """Smoke tests for the project shell."""

    def test_admin_route_is_configured(self) -> None:
        self.assertEqual(reverse("admin:index"), "/admin/")


class ParkingFoundationModelTests(TestCase):
    def test_configured_choices_use_domain_values(self) -> None:
        self.assertEqual(LoyaltyTier.NONE, "none")
        self.assertEqual(LoyaltyTier.SILVER, "silver")
        self.assertEqual(LoyaltyTier.GOLD, "gold")
        self.assertEqual(LoyaltyTier.PLATINUM, "platinum")
        self.assertEqual(SessionStatus.OPEN, "open")
        self.assertEqual(SessionStatus.CLOSED, "closed")
        self.assertEqual(RatePolicy.STANDARD, "standard")
        self.assertEqual(RatePolicy.EARLY_BIRD, "early_bird")
        self.assertEqual(RatePolicy.NIGHT_OWL, "night_owl")
        self.assertEqual(VehicleType.MOTORCYCLE, "motorcycle")
        self.assertEqual(VehicleType.CAR, "car")
        self.assertEqual(VehicleType.BUS, "bus")
        self.assertEqual(SpotType.COMPACT, "compact")
        self.assertEqual(SpotType.LARGE, "large")

    def test_customer_defaults_to_no_loyalty_tier(self) -> None:
        customer = Customer.objects.create()

        self.assertEqual(customer.loyalty_tier, LoyaltyTier.NONE)

    def test_vehicle_registration_is_unique_and_owner_is_optional(self) -> None:
        customer = Customer.objects.create(loyalty_tier=LoyaltyTier.GOLD)
        owned_vehicle = Vehicle.objects.create(
            registration="OWN-001",
            vehicle_type=VehicleType.CAR,
            customer=customer,
        )
        unowned_vehicle = Vehicle.objects.create(
            registration="POOL-001",
            vehicle_type=VehicleType.MOTORCYCLE,
        )

        self.assertIn(owned_vehicle, customer.vehicles.all())
        self.assertIsNone(unowned_vehicle.customer)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Vehicle.objects.create(
                registration="OWN-001",
                vehicle_type=VehicleType.BUS,
            )

    def test_parking_spot_level_and_number_are_unique_together(self) -> None:
        ParkingSpot.objects.create(
            level=1,
            number="A01",
            spot_type=SpotType.COMPACT,
        )
        ParkingSpot.objects.create(
            level=2,
            number="A01",
            spot_type=SpotType.LARGE,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            ParkingSpot.objects.create(
                level=1,
                number="A01",
                spot_type=SpotType.LARGE,
            )

    def test_spot_type_vehicle_compatibility_is_unique_together(self) -> None:
        SpotTypeVehicleCompatibility.objects.create(
            spot_type=SpotType.COMPACT,
            vehicle_type=VehicleType.CAR,
        )
        SpotTypeVehicleCompatibility.objects.create(
            spot_type=SpotType.COMPACT,
            vehicle_type=VehicleType.MOTORCYCLE,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            SpotTypeVehicleCompatibility.objects.create(
                spot_type=SpotType.COMPACT,
                vehicle_type=VehicleType.CAR,
            )

    def test_model_string_representations_are_readable(self) -> None:
        customer = Customer.objects.create(loyalty_tier=LoyaltyTier.SILVER)
        vehicle = Vehicle.objects.create(
            registration="READ-001",
            vehicle_type=VehicleType.BUS,
            customer=customer,
        )
        spot = ParkingSpot.objects.create(
            level=3,
            number="B12",
            spot_type=SpotType.LARGE,
        )
        compatibility = SpotTypeVehicleCompatibility.objects.create(
            spot_type=SpotType.LARGE,
            vehicle_type=VehicleType.BUS,
        )

        self.assertEqual(str(customer), f"Customer {customer.pk} (Silver)")
        self.assertEqual(str(vehicle), "READ-001 (Bus)")
        self.assertEqual(str(spot), "Level 3 Spot B12 (Large)")
        self.assertEqual(str(compatibility), "Large -> Bus")


class ParkingSessionAuditModelTests(TestCase):
    def setUp(self) -> None:
        self.customer = Customer.objects.create(loyalty_tier=LoyaltyTier.SILVER)
        self.vehicle = Vehicle.objects.create(
            registration="AUD-001",
            vehicle_type=VehicleType.CAR,
            customer=self.customer,
        )
        self.spot = ParkingSpot.objects.create(
            level=1,
            number="C01",
            spot_type=SpotType.COMPACT,
        )

    def test_session_defaults_and_optional_fields_match_open_ticket_state(self) -> None:
        session = ParkingSession.objects.create(
            vehicle=self.vehicle,
            spot=self.spot,
            customer=self.customer,
            entered_at=datetime(2026, 9, 28, 8, 15, tzinfo=timezone.utc),
        )

        self.assertEqual(session.status, SessionStatus.OPEN)
        self.assertEqual(session.loyalty_tier_snapshot, LoyaltyTier.NONE)
        self.assertIsNone(session.exited_at)
        self.assertIsNone(session.charged_amount)
        self.assertIsNone(session.selected_evaluation)
        self.assertEqual(session.vehicle, self.vehicle)
        self.assertEqual(session.spot, self.spot)
        self.assertEqual(session.customer, self.customer)

    def test_session_preserves_customer_and_loyalty_snapshot_history(self) -> None:
        session = ParkingSession.objects.create(
            vehicle=self.vehicle,
            spot=self.spot,
            customer=self.customer,
            entered_at=datetime(2026, 9, 28, 8, 15, tzinfo=timezone.utc),
            loyalty_tier_snapshot=self.customer.loyalty_tier,
        )

        new_customer = Customer.objects.create(loyalty_tier=LoyaltyTier.PLATINUM)
        self.vehicle.customer = new_customer
        self.vehicle.save(update_fields=["customer"])
        self.customer.loyalty_tier = LoyaltyTier.GOLD
        self.customer.save(update_fields=["loyalty_tier"])

        session.refresh_from_db()
        self.assertEqual(session.customer, self.customer)
        self.assertEqual(session.loyalty_tier_snapshot, LoyaltyTier.SILVER)
        self.assertEqual(session.vehicle.customer, new_customer)
        self.assertEqual(session.customer.loyalty_tier, LoyaltyTier.GOLD)

    def test_rate_evaluation_stores_policy_audit_details_and_selected_link(self) -> None:
        session = ParkingSession.objects.create(
            vehicle=self.vehicle,
            spot=self.spot,
            customer=self.customer,
            entered_at=datetime(2026, 9, 28, 8, 15, tzinfo=timezone.utc),
            loyalty_tier_snapshot=LoyaltyTier.SILVER,
        )
        evaluation = RateEvaluation.objects.create(
            session=session,
            policy=RatePolicy.EARLY_BIRD,
            applicable=True,
            amount=Decimal("13.50"),
            details={
                "base_amount": "15.00",
                "loyalty_discount": "0.10",
                "vehicle_multiplier": "1.0",
            },
        )
        session.selected_evaluation = evaluation
        session.charged_amount = evaluation.amount
        session.status = SessionStatus.CLOSED
        session.save(update_fields=["selected_evaluation", "charged_amount", "status"])

        session.refresh_from_db()
        evaluation.refresh_from_db()
        self.assertEqual(evaluation.session, session)
        self.assertEqual(session.rate_evaluations.get(), evaluation)
        self.assertEqual(session.selected_evaluation, evaluation)
        self.assertEqual(session.charged_amount, Decimal("13.50"))
        self.assertTrue(evaluation.applicable)
        self.assertEqual(evaluation.policy, RatePolicy.EARLY_BIRD)
        self.assertEqual(evaluation.details["loyalty_discount"], "0.10")
        self.assertIsNotNone(evaluation.created_at)

    def test_rate_evaluation_amount_can_be_null_for_inapplicable_policy(self) -> None:
        session = ParkingSession.objects.create(
            vehicle=self.vehicle,
            spot=self.spot,
            entered_at=datetime(2026, 9, 28, 8, 15, tzinfo=timezone.utc),
        )
        evaluation = RateEvaluation.objects.create(
            session=session,
            policy=RatePolicy.NIGHT_OWL,
            applicable=False,
            details={"reason": "entry_time_outside_window"},
        )

        self.assertFalse(evaluation.applicable)
        self.assertIsNone(evaluation.amount)
        self.assertEqual(evaluation.details["reason"], "entry_time_outside_window")

    def test_public_holiday_date_is_unique_and_string_is_readable(self) -> None:
        holiday = PublicHoliday.objects.create(
            date=date(2026, 12, 25),
            name="Christmas Day",
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            PublicHoliday.objects.create(
                date=date(2026, 12, 25),
                name="Duplicate Christmas",
            )

        self.assertEqual(str(holiday), "Christmas Day (2026-12-25)")

    def test_session_and_evaluation_string_representations_are_readable(self) -> None:
        session = ParkingSession.objects.create(
            vehicle=self.vehicle,
            spot=self.spot,
            entered_at=datetime(2026, 9, 28, 8, 15, tzinfo=timezone.utc),
        )
        evaluation = RateEvaluation.objects.create(
            session=session,
            policy=RatePolicy.STANDARD,
            applicable=True,
            amount=Decimal("12.00"),
        )

        self.assertEqual(str(session), f"Session {session.pk} for AUD-001")
        self.assertEqual(
            str(evaluation),
            f"Standard evaluation for session {session.pk}",
        )


class PricingConstantsAndHelpersTests(TestCase):
    def test_vehicle_multipliers_use_prd_values_as_decimals(self) -> None:
        self.assertEqual(
            VEHICLE_MULTIPLIERS,
            {
                VehicleType.MOTORCYCLE: Decimal("0.8"),
                VehicleType.CAR: Decimal("1.0"),
                VehicleType.BUS: Decimal("2.0"),
            },
        )
        self.assertTrue(
            all(isinstance(amount, Decimal) for amount in VEHICLE_MULTIPLIERS.values()),
        )

    def test_loyalty_discounts_use_prd_values_as_decimals(self) -> None:
        self.assertEqual(
            LOYALTY_DISCOUNTS,
            {
                LoyaltyTier.NONE: Decimal("0"),
                LoyaltyTier.SILVER: Decimal("0.10"),
                LoyaltyTier.GOLD: Decimal("0.20"),
                LoyaltyTier.PLATINUM: Decimal("0.30"),
            },
        )
        self.assertTrue(
            all(isinstance(amount, Decimal) for amount in LOYALTY_DISCOUNTS.values()),
        )

    def test_base_rates_peak_multiplier_and_special_rates_match_prd(self) -> None:
        self.assertEqual(STANDARD_FIRST_HOUR_RATE, Decimal("5.00"))
        self.assertEqual(STANDARD_SECOND_HOUR_RATE, Decimal("3.00"))
        self.assertEqual(STANDARD_SUBSEQUENT_HOUR_RATE, Decimal("2.00"))
        self.assertEqual(
            STANDARD_HOURLY_BASE_RATES,
            (
                Decimal("5.00"),
                Decimal("3.00"),
                Decimal("2.00"),
            ),
        )
        self.assertEqual(PEAK_MULTIPLIER, Decimal("1.5"))
        self.assertEqual(EARLY_BIRD_RATE, Decimal("15.00"))
        self.assertEqual(NIGHT_OWL_RATE, Decimal("8.00"))

    def test_time_windows_use_inclusive_starts_and_exclusive_ends(self) -> None:
        morning_peak = PEAK_WINDOWS[0]

        self.assertTrue(contains_time(time(7, 0), morning_peak))
        self.assertTrue(contains_time(time(9, 59, 59), morning_peak))
        self.assertFalse(contains_time(time(10, 0), morning_peak))
        self.assertTrue(contains_time(time(6, 0), EARLY_BIRD_ENTRY_WINDOW))
        self.assertFalse(contains_time(time(9, 0), EARLY_BIRD_ENTRY_WINDOW))
        self.assertTrue(contains_time(time(15, 30), EARLY_BIRD_EXIT_WINDOW))
        self.assertFalse(contains_time(time(19, 0), EARLY_BIRD_EXIT_WINDOW))
        self.assertTrue(contains_time(time(18, 0), NIGHT_OWL_ENTRY_WINDOW))
        self.assertTrue(contains_time(time.max, NIGHT_OWL_ENTRY_WINDOW))
        self.assertTrue(contains_time(time(5, 0), NIGHT_OWL_EXIT_WINDOW))
        self.assertFalse(contains_time(time(10, 0), NIGHT_OWL_EXIT_WINDOW))

    def test_datetime_interval_overlap_uses_exclusive_ends(self) -> None:
        window_start = datetime(2026, 9, 28, 7, 0, tzinfo=timezone.utc)
        window_end = datetime(2026, 9, 28, 10, 0, tzinfo=timezone.utc)

        self.assertTrue(
            interval_overlaps(
                datetime(2026, 9, 28, 6, 30, tzinfo=timezone.utc),
                datetime(2026, 9, 28, 7, 30, tzinfo=timezone.utc),
                window_start,
                window_end,
            ),
        )
        self.assertFalse(
            interval_overlaps(
                datetime(2026, 9, 28, 6, 0, tzinfo=timezone.utc),
                datetime(2026, 9, 28, 7, 0, tzinfo=timezone.utc),
                window_start,
                window_end,
            ),
        )
        self.assertFalse(
            interval_overlaps(
                datetime(2026, 9, 28, 10, 0, tzinfo=timezone.utc),
                datetime(2026, 9, 28, 11, 0, tzinfo=timezone.utc),
                window_start,
                window_end,
            ),
        )

    def test_window_for_date_preserves_timezone_context(self) -> None:
        start, end = window_for_date(
            date(2026, 9, 28),
            TimeWindow(time(16, 0), time(19, 0)),
            tzinfo=timezone.utc,
        )

        self.assertEqual(start, datetime(2026, 9, 28, 16, 0, tzinfo=timezone.utc))
        self.assertEqual(end, datetime(2026, 9, 28, 19, 0, tzinfo=timezone.utc))

    def test_weekday_detection_excludes_weekends_and_public_holidays(self) -> None:
        monday = date(2026, 9, 28)
        saturday = date(2026, 10, 3)

        self.assertTrue(is_weekday_excluding_public_holidays(monday))
        self.assertFalse(is_weekday_excluding_public_holidays(saturday))

        PublicHoliday.objects.create(date=monday, name="Observed Holiday")

        self.assertFalse(is_weekday_excluding_public_holidays(monday))
        self.assertFalse(
            is_weekday_excluding_public_holidays(
                datetime(2026, 9, 28, 8, 0, tzinfo=timezone.utc),
            ),
        )

    def test_currency_quantization_uses_decimal_cents(self) -> None:
        self.assertEqual(quantize_currency(Decimal("12")), Decimal("12.00"))
        self.assertEqual(quantize_currency(Decimal("12.345")), Decimal("12.35"))
        self.assertEqual(quantize_currency(Decimal("12.344")), Decimal("12.34"))
        self.assertEqual(quantize_currency(Decimal("12.345")).as_tuple().exponent, -2)


class StandardHourlyPolicyTests(TestCase):
    def setUp(self) -> None:
        self.policy = StandardHourlyPolicy()
        self.spot = ParkingSpot.objects.create(
            level=1,
            number="STD-01",
            spot_type=SpotType.COMPACT,
        )
        self.registration_counter = 0

    def create_session(
        self,
        entered_at: datetime,
        exited_at: datetime | None,
        vehicle_type: str = VehicleType.CAR,
    ) -> ParkingSession:
        self.registration_counter += 1
        vehicle = Vehicle.objects.create(
            registration=f"STD-{self.registration_counter:03d}",
            vehicle_type=vehicle_type,
        )
        return ParkingSession.objects.create(
            vehicle=vehicle,
            spot=self.spot,
            entered_at=entered_at,
            exited_at=exited_at,
            status=SessionStatus.CLOSED if exited_at else SessionStatus.OPEN,
        )

    def test_policy_applies_to_sessions_with_valid_entry_and_exit(self) -> None:
        session = self.create_session(
            datetime(2026, 10, 3, 11, 0, tzinfo=timezone.utc),
            datetime(2026, 10, 3, 12, 0, tzinfo=timezone.utc),
        )

        result = self.policy.evaluate(session)

        self.assertEqual(result.policy, RatePolicy.STANDARD)
        self.assertTrue(result.applicable)
        self.assertEqual(result.amount, Decimal("5.00"))
        self.assertEqual(result.details["rounded_hours"], 1)

    def test_policy_rejects_open_missing_and_invalid_exit_sessions(self) -> None:
        open_session = self.create_session(
            datetime(2026, 10, 3, 11, 0, tzinfo=timezone.utc),
            None,
        )
        invalid_session = self.create_session(
            datetime(2026, 10, 3, 11, 0, tzinfo=timezone.utc),
            datetime(2026, 10, 3, 11, 0, tzinfo=timezone.utc),
        )

        open_result = self.policy.evaluate(open_session)
        invalid_result = self.policy.evaluate(invalid_session)

        self.assertFalse(open_result.applicable)
        self.assertIsNone(open_result.amount)
        self.assertEqual(open_result.details["reason"], "missing_exited_at")
        self.assertEqual(open_result.details["hours"], [])
        self.assertFalse(invalid_result.applicable)
        self.assertIsNone(invalid_result.amount)
        self.assertEqual(
            invalid_result.details["reason"],
            "exited_at_must_be_after_entered_at",
        )

    def test_partial_duration_rounds_up_and_final_block_extends_from_entry(self) -> None:
        session = self.create_session(
            datetime(2026, 10, 3, 11, 15, tzinfo=timezone.utc),
            datetime(2026, 10, 3, 12, 16, tzinfo=timezone.utc),
        )

        result = self.policy.evaluate(session)

        self.assertEqual(result.amount, Decimal("8.00"))
        self.assertEqual(result.details["rounded_hours"], 2)
        self.assertEqual(len(result.details["hours"]), 2)
        self.assertEqual(result.details["hours"][0]["start"], "2026-10-03T11:15:00+00:00")
        self.assertEqual(result.details["hours"][1]["start"], "2026-10-03T12:15:00+00:00")
        self.assertEqual(result.details["hours"][1]["end"], "2026-10-03T13:15:00+00:00")

    def test_floating_weekday_peak_example_matches_prd_total(self) -> None:
        session = self.create_session(
            datetime(2026, 9, 28, 6, 30, tzinfo=timezone.utc),
            datetime(2026, 9, 28, 8, 30, tzinfo=timezone.utc),
        )

        result = self.policy.evaluate(session)

        self.assertEqual(result.amount, Decimal("12.00"))
        self.assertEqual(
            [hour["start"] for hour in result.details["hours"]],
            ["2026-09-28T06:30:00+00:00", "2026-09-28T07:30:00+00:00"],
        )
        self.assertEqual(
            [hour["amount"] for hour in result.details["hours"]],
            ["7.50", "4.50"],
        )
        self.assertTrue(all(hour["peak"] for hour in result.details["hours"]))

    def test_base_rate_progression_uses_first_second_and_subsequent_rates(self) -> None:
        session = self.create_session(
            datetime(2026, 10, 3, 11, 0, tzinfo=timezone.utc),
            datetime(2026, 10, 3, 15, 0, tzinfo=timezone.utc),
        )

        result = self.policy.evaluate(session)

        self.assertEqual(result.amount, Decimal("12.00"))
        self.assertEqual(
            [hour["base_rate"] for hour in result.details["hours"]],
            ["5.00", "3.00", "2.00", "2.00"],
        )
        self.assertEqual(
            [hour["amount"] for hour in result.details["hours"]],
            ["5.00", "3.00", "2.00", "2.00"],
        )

    def test_any_partial_overlap_makes_the_whole_block_peak(self) -> None:
        session = self.create_session(
            datetime(2026, 9, 28, 6, 30, tzinfo=timezone.utc),
            datetime(2026, 9, 28, 7, 1, tzinfo=timezone.utc),
        )

        result = self.policy.evaluate(session)

        self.assertEqual(result.amount, Decimal("7.50"))
        self.assertTrue(result.details["hours"][0]["peak"])
        self.assertEqual(result.details["hours"][0]["multiplier"], "1.50")

    def test_peak_windows_use_inclusive_starts_and_exclusive_ends(self) -> None:
        starts_at_peak = self.create_session(
            datetime(2026, 9, 28, 7, 0, tzinfo=timezone.utc),
            datetime(2026, 9, 28, 8, 0, tzinfo=timezone.utc),
        )
        starts_at_peak_end = self.create_session(
            datetime(2026, 9, 28, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 9, 28, 11, 0, tzinfo=timezone.utc),
        )

        peak_result = self.policy.evaluate(starts_at_peak)
        non_peak_result = self.policy.evaluate(starts_at_peak_end)

        self.assertTrue(peak_result.details["hours"][0]["peak"])
        self.assertEqual(peak_result.amount, Decimal("7.50"))
        self.assertFalse(non_peak_result.details["hours"][0]["peak"])
        self.assertEqual(non_peak_result.amount, Decimal("5.00"))

    def test_public_holiday_excludes_weekday_peak_surcharge(self) -> None:
        PublicHoliday.objects.create(date=date(2026, 9, 28), name="Observed Holiday")
        session = self.create_session(
            datetime(2026, 9, 28, 7, 0, tzinfo=timezone.utc),
            datetime(2026, 9, 28, 8, 0, tzinfo=timezone.utc),
        )

        result = self.policy.evaluate(session)

        self.assertFalse(result.details["hours"][0]["peak"])
        self.assertEqual(result.amount, Decimal("5.00"))

    def test_vehicle_multiplier_is_applied_to_each_hourly_block(self) -> None:
        motorcycle_session = self.create_session(
            datetime(2026, 10, 3, 11, 0, tzinfo=timezone.utc),
            datetime(2026, 10, 3, 12, 0, tzinfo=timezone.utc),
            vehicle_type=VehicleType.MOTORCYCLE,
        )
        bus_session = self.create_session(
            datetime(2026, 10, 3, 12, 0, tzinfo=timezone.utc),
            datetime(2026, 10, 3, 13, 0, tzinfo=timezone.utc),
            vehicle_type=VehicleType.BUS,
        )

        motorcycle_result = self.policy.evaluate(motorcycle_session)
        bus_result = self.policy.evaluate(bus_session)

        self.assertEqual(motorcycle_result.amount, Decimal("4.00"))
        self.assertEqual(motorcycle_result.details["hours"][0]["multiplier"], "0.80")
        self.assertEqual(bus_result.amount, Decimal("10.00"))
        self.assertEqual(bus_result.details["hours"][0]["multiplier"], "2.00")


class ParkingAdminConfigurationTests(SimpleTestCase):
    def test_all_parking_models_are_registered_in_admin(self) -> None:
        registered_models = set(django_admin.site._registry)

        self.assertGreaterEqual(
            registered_models,
            {
                Customer,
                Vehicle,
                ParkingSpot,
                SpotTypeVehicleCompatibility,
                ParkingSession,
                RateEvaluation,
                PublicHoliday,
            },
        )

    def test_admin_list_displays_identify_records_without_opening_rows(self) -> None:
        customer_admin = django_admin.site._registry[Customer]
        vehicle_admin = django_admin.site._registry[Vehicle]
        spot_admin = django_admin.site._registry[ParkingSpot]
        compatibility_admin = django_admin.site._registry[SpotTypeVehicleCompatibility]
        session_admin = django_admin.site._registry[ParkingSession]
        evaluation_admin = django_admin.site._registry[RateEvaluation]
        holiday_admin = django_admin.site._registry[PublicHoliday]

        self.assertIn("loyalty_tier", customer_admin.list_display)
        self.assertIn("registration", vehicle_admin.list_display)
        self.assertIn("number", spot_admin.list_display)
        self.assertIn("spot_type", compatibility_admin.list_display)
        self.assertIn("vehicle_registration", session_admin.list_display)
        self.assertIn("selected_evaluation", session_admin.list_display)
        self.assertIn("policy", evaluation_admin.list_display)
        self.assertIn("date", holiday_admin.list_display)

    def test_admin_filters_and_search_fields_support_common_lookups(self) -> None:
        customer_admin = django_admin.site._registry[Customer]
        vehicle_admin = django_admin.site._registry[Vehicle]
        session_admin = django_admin.site._registry[ParkingSession]
        evaluation_admin = django_admin.site._registry[RateEvaluation]
        holiday_admin = django_admin.site._registry[PublicHoliday]

        self.assertIn("registration", vehicle_admin.search_fields)
        self.assertIn("vehicle__registration", session_admin.search_fields)
        self.assertIn("session__vehicle__registration", evaluation_admin.search_fields)
        self.assertIn("status", session_admin.list_filter)
        self.assertIn("policy", evaluation_admin.list_filter)
        self.assertIn("date", holiday_admin.list_filter)
        self.assertIn("loyalty_tier", customer_admin.list_filter)
        self.assertIn("customer__loyalty_tier", vehicle_admin.list_filter)
        self.assertIn("loyalty_tier_snapshot", session_admin.list_filter)

    def test_session_admin_exposes_selected_and_related_evaluations(self) -> None:
        session_admin = django_admin.site._registry[ParkingSession]

        self.assertIn("selected_evaluation", session_admin.list_display)
        self.assertIn("selected_evaluation", session_admin.readonly_fields)
        self.assertIn(RateEvaluationInline, session_admin.inlines)
        self.assertEqual(
            RateEvaluationInline.readonly_fields,
            ("policy", "applicable", "amount", "details", "created_at"),
        )
        self.assertTrue(RateEvaluationInline.show_change_link)
        self.assertFalse(RateEvaluationInline.can_delete)
