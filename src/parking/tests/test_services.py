"""Tests for the ticket entry and exit application services."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone as django_timezone

from parking.models import (
    Customer,
    LoyaltyTier,
    ParkingSession,
    ParkingSpot,
    RateEvaluation,
    RatePolicy,
    SessionStatus,
    SpotType,
    SpotTypeVehicleCompatibility,
    Vehicle,
    VehicleType,
)
from parking.pricing import NoApplicableRatePolicyError
from parking.services import (
    IncompatibleSpotError,
    ParkingServiceError,
    SessionExitError,
    record_entry,
    record_exit,
)


class ParkingServiceTestBase(TestCase):
    """Shared fixtures: a car, a compatible compact spot, and a customer."""

    def setUp(self) -> None:
        self.customer = Customer.objects.create(loyalty_tier=LoyaltyTier.GOLD)
        self.vehicle = Vehicle.objects.create(
            registration="SVC-001",
            vehicle_type=VehicleType.CAR,
            customer=self.customer,
        )
        self.spot = ParkingSpot.objects.create(
            level=1,
            number="SVC-01",
            spot_type=SpotType.COMPACT,
        )
        SpotTypeVehicleCompatibility.objects.create(
            spot_type=SpotType.COMPACT,
            vehicle_type=VehicleType.CAR,
        )
        # Saturday 2026-10-03: no peak surcharge, no special windows.
        self.entered_at = datetime(2026, 10, 3, 11, 0, tzinfo=timezone.utc)
        self.exited_at = datetime(2026, 10, 3, 12, 0, tzinfo=timezone.utc)


class RecordEntryServiceTests(ParkingServiceTestBase):
    def test_entry_creates_open_session_with_vehicle_spot_and_timestamp(self) -> None:
        session = record_entry(
            self.vehicle,
            self.spot,
            entered_at=self.entered_at,
        )

        self.assertIsNotNone(session.pk)
        self.assertEqual(session.status, SessionStatus.OPEN)
        self.assertEqual(session.vehicle, self.vehicle)
        self.assertEqual(session.spot, self.spot)
        self.assertEqual(session.entered_at, self.entered_at)
        self.assertIsNone(session.exited_at)
        self.assertIsNone(session.charged_amount)
        self.assertIsNone(session.selected_evaluation)
        self.assertEqual(ParkingSession.objects.count(), 1)

    def test_entry_defaults_entered_at_to_now(self) -> None:
        session = record_entry(self.vehicle, self.spot)

        self.assertIsNotNone(session.entered_at)
        self.assertLess(
            abs((django_timezone.now() - session.entered_at).total_seconds()),
            5,
        )

    def test_entry_snapshots_customer_loyalty_tier_at_entry_time(self) -> None:
        session = record_entry(
            self.vehicle,
            self.spot,
            customer=self.customer,
            entered_at=self.entered_at,
        )

        self.assertEqual(session.customer, self.customer)
        self.assertEqual(session.loyalty_tier_snapshot, LoyaltyTier.GOLD)

        # Later tier changes must not affect the historical snapshot.
        self.customer.loyalty_tier = LoyaltyTier.PLATINUM
        self.customer.save(update_fields=["loyalty_tier"])
        session.refresh_from_db()
        self.assertEqual(session.loyalty_tier_snapshot, LoyaltyTier.GOLD)

    def test_entry_defaults_customer_to_vehicle_owner(self) -> None:
        session = record_entry(self.vehicle, self.spot, entered_at=self.entered_at)

        self.assertEqual(session.customer, self.customer)
        self.assertEqual(session.loyalty_tier_snapshot, LoyaltyTier.GOLD)

    def test_entry_without_customer_defaults_loyalty_snapshot_to_none(self) -> None:
        unowned_vehicle = Vehicle.objects.create(
            registration="SVC-POOL",
            vehicle_type=VehicleType.CAR,
        )

        session = record_entry(unowned_vehicle, self.spot, entered_at=self.entered_at)

        self.assertIsNone(session.customer)
        self.assertEqual(session.loyalty_tier_snapshot, LoyaltyTier.NONE)

    def test_entry_rejects_incompatible_vehicle_and_spot(self) -> None:
        bus = Vehicle.objects.create(
            registration="SVC-BUS",
            vehicle_type=VehicleType.BUS,
        )

        with self.assertRaisesRegex(
            IncompatibleSpotError,
            "not allowed in spot type",
        ):
            record_entry(bus, self.spot, entered_at=self.entered_at)

        self.assertEqual(ParkingSession.objects.count(), 0)

    def test_entry_rejects_missing_compatibility_row(self) -> None:
        large_spot = ParkingSpot.objects.create(
            level=2,
            number="SVC-02",
            spot_type=SpotType.LARGE,
        )

        with self.assertRaises(IncompatibleSpotError):
            record_entry(self.vehicle, large_spot, entered_at=self.entered_at)

        self.assertEqual(ParkingSession.objects.count(), 0)

    def test_service_errors_share_common_base(self) -> None:
        self.assertTrue(issubclass(IncompatibleSpotError, ParkingServiceError))
        self.assertTrue(issubclass(SessionExitError, ParkingServiceError))


class RecordExitServiceTests(ParkingServiceTestBase):
    def create_open_session(self) -> ParkingSession:
        return record_entry(
            self.vehicle,
            self.spot,
            customer=self.customer,
            entered_at=self.entered_at,
        )

    def test_exit_persists_evaluations_selected_charge_and_closed_status(self) -> None:
        session = self.create_open_session()

        exited = record_exit(session, exited_at=self.exited_at)

        self.assertEqual(exited, session)
        session.refresh_from_db()
        self.assertEqual(session.status, SessionStatus.CLOSED)
        self.assertEqual(session.exited_at, self.exited_at)

        evaluations = {
            evaluation.policy: evaluation
            for evaluation in RateEvaluation.objects.filter(session=session)
        }
        self.assertEqual(
            set(evaluations),
            {RatePolicy.STANDARD, RatePolicy.EARLY_BIRD, RatePolicy.NIGHT_OWL},
        )
        self.assertTrue(evaluations[RatePolicy.STANDARD].applicable)
        self.assertFalse(evaluations[RatePolicy.EARLY_BIRD].applicable)
        self.assertFalse(evaluations[RatePolicy.NIGHT_OWL].applicable)

        self.assertIsNotNone(session.selected_evaluation)
        self.assertEqual(session.selected_evaluation.policy, RatePolicy.STANDARD)
        self.assertEqual(session.charged_amount, Decimal("5.00"))
        self.assertEqual(
            session.selected_evaluation,
            evaluations[RatePolicy.STANDARD],
        )

    def test_exit_defaults_exited_at_to_now(self) -> None:
        session = record_entry(
            self.vehicle,
            self.spot,
            customer=self.customer,
            entered_at=django_timezone.now() - timedelta(hours=1),
        )

        record_exit(session)

        session.refresh_from_db()
        self.assertIsNotNone(session.exited_at)
        self.assertLess(
            abs((django_timezone.now() - session.exited_at).total_seconds()),
            5,
        )

    def test_repeated_exit_is_idempotent_noop(self) -> None:
        session = self.create_open_session()
        record_exit(session, exited_at=self.exited_at)
        first_evaluation_ids = set(
            RateEvaluation.objects.filter(session=session).values_list(
                "id",
                flat=True,
            ),
        )
        charged_amount = session.charged_amount
        selected_evaluation = session.selected_evaluation

        returned = record_exit(session, exited_at=datetime(2026, 10, 3, 13, 0, tzinfo=timezone.utc))

        self.assertEqual(returned, session)
        session.refresh_from_db()
        self.assertEqual(session.status, SessionStatus.CLOSED)
        self.assertEqual(session.exited_at, self.exited_at)
        self.assertEqual(session.charged_amount, charged_amount)
        self.assertEqual(session.selected_evaluation, selected_evaluation)
        self.assertEqual(
            set(
                RateEvaluation.objects.filter(session=session).values_list(
                    "id",
                    flat=True,
                ),
            ),
            first_evaluation_ids,
        )
        self.assertEqual(RateEvaluation.objects.filter(session=session).count(), 3)

    def test_exit_rejects_unsaved_session(self) -> None:
        unsaved = ParkingSession(
            vehicle=self.vehicle,
            spot=self.spot,
            entered_at=self.entered_at,
        )

        with self.assertRaisesRegex(SessionExitError, "unsaved"):
            record_exit(unsaved, exited_at=self.exited_at)

    def test_exit_rejects_session_missing_entered_at(self) -> None:
        session = self.create_open_session()
        session.entered_at = None

        with self.assertRaisesRegex(SessionExitError, "entered_at"):
            record_exit(session, exited_at=self.exited_at)

        session.refresh_from_db()
        self.assertEqual(session.status, SessionStatus.OPEN)
        self.assertIsNone(session.exited_at)

    def test_exit_rejects_session_missing_vehicle(self) -> None:
        session = self.create_open_session()
        session.vehicle = None

        with self.assertRaisesRegex(SessionExitError, "vehicle"):
            record_exit(session, exited_at=self.exited_at)

    def test_exit_rejects_session_missing_spot(self) -> None:
        session = self.create_open_session()
        session.spot = None

        with self.assertRaisesRegex(SessionExitError, "spot"):
            record_exit(session, exited_at=self.exited_at)

    def test_exit_rolls_back_when_no_policy_applies(self) -> None:
        session = self.create_open_session()

        with self.assertRaises(NoApplicableRatePolicyError):
            record_exit(session, exited_at=self.entered_at)

        session.refresh_from_db()
        self.assertEqual(session.status, SessionStatus.OPEN)
        self.assertIsNone(session.exited_at)
        self.assertIsNone(session.charged_amount)
        self.assertIsNone(session.selected_evaluation)
        self.assertEqual(RateEvaluation.objects.filter(session=session).count(), 0)
