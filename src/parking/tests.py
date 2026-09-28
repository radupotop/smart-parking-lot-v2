"""Tests for the parking app."""

from datetime import date, datetime, timezone
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
