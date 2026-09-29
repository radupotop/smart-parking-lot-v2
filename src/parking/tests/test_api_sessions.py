"""API tests for the /api/sessions/ endpoint (create + read only)."""

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


class SessionApiTestBase(APITestCase):
    """Shared fixtures: a GOLD customer, their CAR, a COMPACT spot, and the
    COMPACT/CAR compatibility row that lets the car park there."""

    def setUp(self) -> None:
        self.customer = Customer.objects.create(loyalty_tier=LoyaltyTier.GOLD)
        self.vehicle = Vehicle.objects.create(
            registration="SES-001",
            vehicle_type=VehicleType.CAR,
            customer=self.customer,
        )
        self.spot = ParkingSpot.objects.create(
            level=1,
            number="S1",
            spot_type=SpotType.COMPACT,
        )
        SpotTypeVehicleCompatibility.objects.create(
            spot_type=SpotType.COMPACT,
            vehicle_type=VehicleType.CAR,
        )


class SessionCreateApiTests(SessionApiTestBase):
    def test_create_session_returns_open_ticket(self) -> None:
        response = self.client.post(
            "/api/sessions/",
            {
                "vehicle": self.vehicle.pk,
                "spot": self.spot.pk,
                "entered_at": "2026-10-03T11:00:00Z",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["status"], SessionStatus.OPEN)
        self.assertIsNone(response.data["exited_at"])
        self.assertIsNone(response.data["charged_amount"])
        self.assertEqual(response.data["customer"]["id"], self.customer.pk)
        self.assertEqual(response.data["loyalty_tier_snapshot"], LoyaltyTier.GOLD)
        self.assertEqual(response.data["vehicle"]["id"], self.vehicle.pk)
        self.assertEqual(response.data["spot"]["id"], self.spot.pk)
        self.assertEqual(response.data["entered_at"], "2026-10-03T11:00:00Z")
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

        self.assertEqual(ParkingSession.objects.count(), 1)

    def test_create_session_defaults_customer_and_entered_at(self) -> None:
        response = self.client.post(
            "/api/sessions/",
            {"vehicle": self.vehicle.pk, "spot": self.spot.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["customer"]["id"], self.customer.pk)
        self.assertIsNotNone(response.data["entered_at"])

    def test_create_session_with_explicit_customer_uses_its_tier(self) -> None:
        silver_customer = Customer.objects.create(loyalty_tier=LoyaltyTier.SILVER)

        response = self.client.post(
            "/api/sessions/",
            {
                "vehicle": self.vehicle.pk,
                "spot": self.spot.pk,
                "customer": silver_customer.pk,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["customer"]["id"], silver_customer.pk)
        self.assertEqual(response.data["loyalty_tier_snapshot"], LoyaltyTier.SILVER)

    def test_create_session_rejects_incompatible_vehicle_and_spot(self) -> None:
        bus = Vehicle.objects.create(
            registration="SES-002",
            vehicle_type=VehicleType.BUS,
        )

        response = self.client.post(
            "/api/sessions/",
            {"vehicle": bus.pk, "spot": self.spot.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertEqual(ParkingSession.objects.count(), 0)

    def test_create_session_rejects_unknown_vehicle_spot_or_invalid_entered_at(self) -> None:
        unknown_vehicle = self.client.post(
            "/api/sessions/",
            {"vehicle": 99999, "spot": self.spot.pk},
            format="json",
        )
        self.assertEqual(unknown_vehicle.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("vehicle", unknown_vehicle.data)

        unknown_spot = self.client.post(
            "/api/sessions/",
            {"vehicle": self.vehicle.pk, "spot": 99999},
            format="json",
        )
        self.assertEqual(unknown_spot.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("spot", unknown_spot.data)

        invalid_entered_at = self.client.post(
            "/api/sessions/",
            {
                "vehicle": self.vehicle.pk,
                "spot": self.spot.pk,
                "entered_at": "not-a-date",
            },
            format="json",
        )
        self.assertEqual(invalid_entered_at.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("entered_at", invalid_entered_at.data)

        self.assertEqual(ParkingSession.objects.count(), 0)

    def test_create_session_rejects_missing_required_fields(self) -> None:
        response = self.client.post("/api/sessions/", {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("vehicle", response.data)
        self.assertIn("spot", response.data)
        self.assertEqual(ParkingSession.objects.count(), 0)


class SessionReadApiTests(SessionApiTestBase):
    def test_list_and_retrieve_sessions(self) -> None:
        older = self.client.post(
            "/api/sessions/",
            {
                "vehicle": self.vehicle.pk,
                "spot": self.spot.pk,
                "entered_at": "2026-10-03T09:00:00Z",
            },
            format="json",
        )
        self.assertEqual(older.status_code, status.HTTP_201_CREATED)
        older_session = ParkingSession.objects.get(pk=older.data["id"])

        second_vehicle = Vehicle.objects.create(
            registration="SES-002",
            vehicle_type=VehicleType.CAR,
            customer=self.customer,
        )
        newer = self.client.post(
            "/api/sessions/",
            {
                "vehicle": second_vehicle.pk,
                "spot": self.spot.pk,
                "entered_at": "2026-10-03T11:00:00Z",
            },
            format="json",
        )
        self.assertEqual(newer.status_code, status.HTTP_201_CREATED)
        newer_session = ParkingSession.objects.get(pk=newer.data["id"])

        list_response = self.client.get("/api/sessions/")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [row["id"] for row in list_response.data],
            [newer_session.pk, older_session.pk],
        )

        retrieve_response = self.client.get(f"/api/sessions/{older_session.pk}/")
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data["id"], older_session.pk)
        self.assertEqual(retrieve_response.data["status"], SessionStatus.OPEN)
        self.assertEqual(retrieve_response.data["vehicle"]["id"], self.vehicle.pk)
        self.assertEqual(retrieve_response.data["spot"]["id"], self.spot.pk)
        self.assertIn("created_at", retrieve_response.data)
        self.assertIn("updated_at", retrieve_response.data)


class SessionMethodRestrictionApiTests(SessionApiTestBase):
    def test_update_and_delete_session_are_not_allowed(self) -> None:
        created = self.client.post(
            "/api/sessions/",
            {"vehicle": self.vehicle.pk, "spot": self.spot.pk},
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        session_pk = created.data["id"]

        put_response = self.client.put(
            f"/api/sessions/{session_pk}/",
            {"status": SessionStatus.CLOSED},
            format="json",
        )
        patch_response = self.client.patch(
            f"/api/sessions/{session_pk}/",
            {"status": SessionStatus.CLOSED},
            format="json",
        )
        delete_response = self.client.delete(f"/api/sessions/{session_pk}/")

        self.assertEqual(put_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(patch_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(delete_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        session = ParkingSession.objects.get(pk=session_pk)
        self.assertEqual(session.status, SessionStatus.OPEN)
        self.assertEqual(ParkingSession.objects.count(), 1)
