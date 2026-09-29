"""API tests for the /api/sessions/<id>/exit/ endpoint (POST only)."""

from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from parking.models import (
    Customer,
    LoyaltyTier,
    ParkingSession,
    ParkingSpot,
    SessionStatus,
    SpotType,
    SpotTypeVehicleCompatibility,
    Vehicle,
    VehicleType,
)


class SessionExitApiTestBase(APITestCase):
    """Shared fixtures: a GOLD customer, their CAR, a COMPACT spot, and the
    COMPACT/CAR compatibility row that lets the car park there."""

    def setUp(self) -> None:
        self.customer = Customer.objects.create(loyalty_tier=LoyaltyTier.GOLD)
        self.vehicle = Vehicle.objects.create(
            registration="EXIT-001",
            vehicle_type=VehicleType.CAR,
            customer=self.customer,
        )
        self.spot = ParkingSpot.objects.create(
            level=1,
            number="E1",
            spot_type=SpotType.COMPACT,
        )
        SpotTypeVehicleCompatibility.objects.get_or_create(
            spot_type=SpotType.COMPACT,
            vehicle_type=VehicleType.CAR,
        )

    def create_open_session(self, entered_at: str = "2026-10-03T11:00:00Z") -> dict:
        response = self.client.post(
            "/api/sessions/",
            {
                "vehicle": self.vehicle.pk,
                "spot": self.spot.pk,
                "entered_at": entered_at,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data


class SessionExitSuccessApiTests(SessionExitApiTestBase):
    def test_exit_open_session_returns_closed_session_with_charge(self) -> None:
        session_data = self.create_open_session("2026-10-03T11:00:00Z")
        session_pk = session_data["id"]

        response = self.client.post(
            f"/api/sessions/{session_pk}/exit/",
            {"exited_at": "2026-10-03T12:00:00Z"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], SessionStatus.CLOSED)
        self.assertEqual(response.data["exited_at"], "2026-10-03T12:00:00Z")
        self.assertIsNotNone(response.data["charged_amount"])
        self.assertIsNotNone(response.data["selected_evaluation"])
        self.assertIsInstance(response.data["rate_evaluations"], list)
        self.assertGreater(len(response.data["rate_evaluations"]), 0)

        session = ParkingSession.objects.get(pk=session_pk)
        self.assertEqual(session.status, SessionStatus.CLOSED)
        self.assertEqual(
            session.charged_amount, Decimal(response.data["charged_amount"])
        )

    def test_exit_session_defaults_exited_at_to_now(self) -> None:
        entered_at = (
            (timezone.now() - timedelta(hours=1)).isoformat().replace(
                "+00:00", "Z"
            )
        )
        session_data = self.create_open_session(entered_at)
        session_pk = session_data["id"]

        response = self.client.post(
            f"/api/sessions/{session_pk}/exit/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], SessionStatus.CLOSED)
        self.assertIsNotNone(response.data["exited_at"])


class SessionExitValidationApiTests(SessionExitApiTestBase):
    def test_exit_session_rejects_invalid_exited_at(self) -> None:
        session_data = self.create_open_session()
        session_pk = session_data["id"]

        response = self.client.post(
            f"/api/sessions/{session_pk}/exit/",
            {"exited_at": "not-a-date"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("exited_at", response.data)

        session = ParkingSession.objects.get(pk=session_pk)
        self.assertEqual(session.status, SessionStatus.OPEN)

    def test_exit_session_rejects_exited_at_before_entered_at(self) -> None:
        session_data = self.create_open_session("2026-10-03T11:00:00Z")
        session_pk = session_data["id"]

        response = self.client.post(
            f"/api/sessions/{session_pk}/exit/",
            {"exited_at": "2026-10-03T10:00:00Z"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("detail", response.data)

        session = ParkingSession.objects.get(pk=session_pk)
        self.assertEqual(session.status, SessionStatus.OPEN)

    def test_exit_stay_longer_than_24_hours_is_charged_by_standard_hourly(
        self,
    ) -> None:
        # The 24h cap invalidates only the special rates (Early Bird / Night
        # Owl), so Standard Hourly still charges a stay longer than 24 hours.
        session_data = self.create_open_session("2026-10-01T10:00:00Z")
        session_pk = session_data["id"]

        response = self.client.post(
            f"/api/sessions/{session_pk}/exit/",
            {"exited_at": "2026-10-02T11:00:00Z"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], SessionStatus.CLOSED)
        self.assertIsNotNone(response.data["charged_amount"])

        session = ParkingSession.objects.get(pk=session_pk)
        self.assertEqual(session.status, SessionStatus.CLOSED)


class SessionExitIdempotencyApiTests(SessionExitApiTestBase):
    def test_exit_already_closed_session_is_idempotent(self) -> None:
        session_data = self.create_open_session("2026-10-03T11:00:00Z")
        session_pk = session_data["id"]

        first = self.client.post(
            f"/api/sessions/{session_pk}/exit/",
            {"exited_at": "2026-10-03T12:00:00Z"},
            format="json",
        )
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        original_exited_at = first.data["exited_at"]
        original_charged_amount = first.data["charged_amount"]
        original_evaluation_count = len(first.data["rate_evaluations"])

        second = self.client.post(
            f"/api/sessions/{session_pk}/exit/",
            {"exited_at": "2026-10-03T13:00:00Z"},
            format="json",
        )

        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(second.data["status"], SessionStatus.CLOSED)
        self.assertEqual(second.data["exited_at"], original_exited_at)
        self.assertEqual(second.data["charged_amount"], original_charged_amount)
        self.assertEqual(
            len(second.data["rate_evaluations"]), original_evaluation_count
        )

        session = ParkingSession.objects.get(pk=session_pk)
        self.assertEqual(
            session.rate_evaluations.count(), original_evaluation_count
        )


class SessionExitErrorApiTests(SessionExitApiTestBase):
    def test_exit_missing_session_returns_404(self) -> None:
        response = self.client.post(
            "/api/sessions/99999/exit/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SessionExitMethodRestrictionApiTests(SessionExitApiTestBase):
    def test_exit_endpoint_rejects_non_post_methods(self) -> None:
        session_data = self.create_open_session()
        session_pk = session_data["id"]

        get_response = self.client.get(f"/api/sessions/{session_pk}/exit/")
        put_response = self.client.put(
            f"/api/sessions/{session_pk}/exit/",
            {},
            format="json",
        )

        self.assertEqual(get_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(put_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        session = ParkingSession.objects.get(pk=session_pk)
        self.assertEqual(session.status, SessionStatus.OPEN)
