"""API tests for the parking REST endpoints."""

from datetime import datetime, timezone

from rest_framework import status
from rest_framework.test import APITestCase

from parking.models import (
    Customer,
    LoyaltyTier,
    ParkingSession,
    ParkingSpot,
    RatePolicy,
    SpotType,
    SpotTypeVehicleCompatibility,
    Vehicle,
    VehicleType,
)
from parking.services import record_exit


class ParkingAPITestBase(APITestCase):
    """Shared fixtures: a car, a compatible compact spot, and a customer."""

    def setUp(self) -> None:
        self.customer = Customer.objects.create(loyalty_tier=LoyaltyTier.GOLD)
        self.vehicle = Vehicle.objects.create(
            registration="API-001",
            vehicle_type=VehicleType.CAR,
            customer=self.customer,
        )
        self.spot = ParkingSpot.objects.create(
            level=1,
            number="API-01",
            spot_type=SpotType.COMPACT,
        )
        SpotTypeVehicleCompatibility.objects.get_or_create(
            spot_type=SpotType.COMPACT,
            vehicle_type=VehicleType.CAR,
        )
        # Saturday 2026-10-03: no peak surcharge, no special windows.
        self.entered_at = datetime(2026, 10, 3, 11, 0, tzinfo=timezone.utc)
        self.exited_at = datetime(2026, 10, 3, 12, 0, tzinfo=timezone.utc)

    def create_session_via_api(self, **overrides) -> dict:
        payload = {
            "vehicle": self.vehicle.pk,
            "spot": self.spot.pk,
            "entered_at": self.entered_at.isoformat().replace("+00:00", "Z"),
        }
        payload.update(overrides)
        response = self.client.post("/api/sessions/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED, response.data
        return response.data


class CustomerApiTests(ParkingAPITestBase):
    def test_create_customer(self) -> None:
        response = self.client.post(
            "/api/customers/",
            {"loyalty_tier": LoyaltyTier.SILVER},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["loyalty_tier"], LoyaltyTier.SILVER)
        self.assertEqual(Customer.objects.count(), 2)

    def test_list_customers(self) -> None:
        response = self.client.get("/api/customers/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.customer.pk)


class VehicleApiTests(ParkingAPITestBase):
    def test_create_vehicle(self) -> None:
        response = self.client.post(
            "/api/vehicles/",
            {
                "registration": "API-NEW",
                "vehicle_type": VehicleType.MOTORCYCLE,
                "customer": self.customer.pk,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["registration"], "API-NEW")
        self.assertEqual(response.data["customer"], self.customer.pk)

    def test_create_vehicle_rejects_duplicate_registration(self) -> None:
        response = self.client.post(
            "/api/vehicles/",
            {
                "registration": self.vehicle.registration,
                "vehicle_type": VehicleType.CAR,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("registration", response.data)

    def test_create_vehicle_rejects_missing_data(self) -> None:
        response = self.client.post("/api/vehicles/", {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("registration", response.data)
        self.assertIn("vehicle_type", response.data)


class ParkingSpotApiTests(ParkingAPITestBase):
    def test_create_spot(self) -> None:
        response = self.client.post(
            "/api/spots/",
            {"level": 2, "number": "API-02", "spot_type": SpotType.LARGE},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["level"], 2)
        self.assertEqual(response.data["spot_type"], SpotType.LARGE)

    def test_create_spot_rejects_duplicate_level_number(self) -> None:
        response = self.client.post(
            "/api/spots/",
            {"level": self.spot.level, "number": self.spot.number, "spot_type": SpotType.LARGE},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_spot_rejects_missing_data(self) -> None:
        response = self.client.post("/api/spots/", {"level": 3}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("number", response.data)
        self.assertIn("spot_type", response.data)


class SessionCreateApiTests(ParkingAPITestBase):
    def test_entry_creates_open_session(self) -> None:
        data = self.create_session_via_api()

        self.assertEqual(data["status"], "open")
        self.assertEqual(data["vehicle"]["registration"], self.vehicle.registration)
        self.assertEqual(data["vehicle"]["vehicle_type"], VehicleType.CAR)
        self.assertEqual(data["spot"]["level"], self.spot.level)
        self.assertEqual(data["spot"]["number"], self.spot.number)
        self.assertEqual(data["spot"]["spot_type"], SpotType.COMPACT)
        self.assertEqual(data["customer"]["id"], self.customer.pk)
        self.assertEqual(data["loyalty_tier_snapshot"], LoyaltyTier.GOLD)
        self.assertIsNone(data["exited_at"])
        self.assertIsNone(data["charged_amount"])
        self.assertIsNone(data["selected_evaluation"])
        self.assertEqual(data["rate_evaluations"], [])
        self.assertEqual(ParkingSession.objects.count(), 1)

    def test_entry_rejects_incompatible_spot(self) -> None:
        bus = Vehicle.objects.create(
            registration="API-BUS",
            vehicle_type=VehicleType.BUS,
        )

        response = self.client.post(
            "/api/sessions/",
            {"vehicle": bus.pk, "spot": self.spot.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("not allowed in spot type", response.data["detail"])
        self.assertEqual(ParkingSession.objects.count(), 0)

    def test_entry_rejects_missing_data(self) -> None:
        response = self.client.post("/api/sessions/", {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("vehicle", response.data)
        self.assertIn("spot", response.data)

    def test_entry_rejects_unknown_vehicle(self) -> None:
        response = self.client.post(
            "/api/sessions/",
            {"vehicle": 9999, "spot": self.spot.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("vehicle", response.data)

    def test_entry_rejects_invalid_entered_at(self) -> None:
        response = self.client.post(
            "/api/sessions/",
            {
                "vehicle": self.vehicle.pk,
                "spot": self.spot.pk,
                "entered_at": "not-a-timestamp",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("entered_at", response.data)


class SessionExitApiTests(ParkingAPITestBase):
    def test_exit_records_exit_data_and_returns_final_charge(self) -> None:
        created = self.create_session_via_api()

        response = self.client.post(
            f"/api/sessions/{created['id']}/exit/",
            {"exited_at": self.exited_at.isoformat().replace("+00:00", "Z")},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "closed")
        self.assertEqual(
            response.data["exited_at"],
            self.exited_at.isoformat().replace("+00:00", "Z"),
        )
        self.assertEqual(response.data["charged_amount"], "5.00")
        self.assertEqual(response.data["selected_evaluation"]["policy"], RatePolicy.STANDARD)
        self.assertTrue(response.data["selected_evaluation"]["applicable"])
        self.assertEqual(response.data["selected_evaluation"]["amount"], "5.00")
        self.assertEqual(len(response.data["rate_evaluations"]), 3)

    def test_exit_is_idempotent_on_closed_session(self) -> None:
        created = self.create_session_via_api()
        first = self.client.post(
            f"/api/sessions/{created['id']}/exit/",
            {"exited_at": self.exited_at.isoformat().replace("+00:00", "Z")},
            format="json",
        )

        second = self.client.post(
            f"/api/sessions/{created['id']}/exit/",
            {},
            format="json",
        )

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(second.data["charged_amount"], first.data["charged_amount"])
        self.assertEqual(second.data["exited_at"], first.data["exited_at"])
        self.assertEqual(second.data["status"], "closed")
        self.assertEqual(len(second.data["rate_evaluations"]), 3)

    def test_exit_returns_422_when_no_policy_applies(self) -> None:
        created = self.create_session_via_api()

        # exited_at == entered_at: no policy can price a zero-length stay.
        response = self.client.post(
            f"/api/sessions/{created['id']}/exit/",
            {"exited_at": self.entered_at.isoformat().replace("+00:00", "Z")},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("No applicable rate policy", response.data["detail"])

        session = ParkingSession.objects.get(pk=created["id"])
        self.assertEqual(session.status, "open")
        self.assertIsNone(session.exited_at)

    def test_exit_rejects_invalid_exited_at(self) -> None:
        created = self.create_session_via_api()

        response = self.client.post(
            f"/api/sessions/{created['id']}/exit/",
            {"exited_at": "not-a-timestamp"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("exited_at", response.data)

    def test_exit_rejects_missing_session(self) -> None:
        response = self.client.post(
            "/api/sessions/9999/exit/", {}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SessionReadApiTests(ParkingAPITestBase):
    def test_list_and_retrieve_include_audit_data_after_exit(self) -> None:
        created = self.create_session_via_api()
        record_exit(
            ParkingSession.objects.get(pk=created["id"]),
            exited_at=self.exited_at,
        )

        list_response = self.client.get("/api/sessions/")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)

        retrieve_response = self.client.get(f"/api/sessions/{created['id']}/")
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        data = retrieve_response.data

        self.assertEqual(data["status"], "closed")
        self.assertEqual(data["charged_amount"], "5.00")
        self.assertEqual(data["selected_evaluation"]["policy"], RatePolicy.STANDARD)
        self.assertEqual(data["vehicle"]["registration"], self.vehicle.registration)
        self.assertEqual(data["spot"]["number"], self.spot.number)

        evaluations = {
            evaluation["policy"]: evaluation for evaluation in data["rate_evaluations"]
        }
        self.assertEqual(
            set(evaluations),
            {RatePolicy.STANDARD, RatePolicy.EARLY_BIRD, RatePolicy.NIGHT_OWL},
        )
        self.assertTrue(evaluations[RatePolicy.STANDARD]["applicable"])
        self.assertEqual(evaluations[RatePolicy.STANDARD]["amount"], "5.00")
        self.assertFalse(evaluations[RatePolicy.EARLY_BIRD]["applicable"])
        self.assertIsNone(evaluations[RatePolicy.EARLY_BIRD]["amount"])
        self.assertFalse(evaluations[RatePolicy.NIGHT_OWL]["applicable"])

    def test_retrieve_open_session_before_exit(self) -> None:
        created = self.create_session_via_api()

        response = self.client.get(f"/api/sessions/{created['id']}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "open")
        self.assertIsNone(response.data["charged_amount"])
        self.assertIsNone(response.data["selected_evaluation"])
        self.assertEqual(response.data["rate_evaluations"], [])

    def test_session_update_and_delete_are_not_allowed(self) -> None:
        created = self.create_session_via_api()
        url = f"/api/sessions/{created['id']}/"

        put_response = self.client.put(url, {"status": "closed"}, format="json")
        patch_response = self.client.patch(
            url, {"charged_amount": "0.01"}, format="json"
        )
        delete_response = self.client.delete(url)

        self.assertEqual(put_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(patch_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(delete_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(ParkingSession.objects.count(), 1)
