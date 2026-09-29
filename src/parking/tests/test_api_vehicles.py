"""API tests for the /api/vehicles/ endpoint (full CRUD)."""

from rest_framework import status
from rest_framework.test import APITestCase

from parking.models import Customer, LoyaltyTier, Vehicle, VehicleType


class VehicleCrudApiTestBase(APITestCase):
    """Shared fixtures: one customer and one persisted vehicle."""

    def setUp(self) -> None:
        self.customer = Customer.objects.create(loyalty_tier=LoyaltyTier.SILVER)
        self.vehicle = Vehicle.objects.create(
            registration="VEH-001",
            vehicle_type=VehicleType.CAR,
            customer=self.customer,
        )


class VehicleCreateApiTests(VehicleCrudApiTestBase):
    def test_create_vehicle_returns_created_representation(self) -> None:
        response = self.client.post(
            "/api/vehicles/",
            {"registration": "VEH-002", "vehicle_type": VehicleType.BUS, "customer": self.customer.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["registration"], "VEH-002")
        self.assertEqual(response.data["vehicle_type"], VehicleType.BUS)
        self.assertEqual(response.data["customer"], self.customer.pk)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

        created = Vehicle.objects.get(pk=response.data["id"])
        self.assertEqual(created.registration, "VEH-002")
        self.assertEqual(created.vehicle_type, VehicleType.BUS)
        self.assertEqual(created.customer, self.customer)
        self.assertEqual(Vehicle.objects.count(), 2)

    def test_create_vehicle_without_customer_is_accepted(self) -> None:
        response = self.client.post(
            "/api/vehicles/",
            {"registration": "VEH-003", "vehicle_type": VehicleType.MOTORCYCLE},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["customer"], None)

        created = Vehicle.objects.get(pk=response.data["id"])
        self.assertIsNone(created.customer)

    def test_create_vehicle_rejects_duplicate_registration(self) -> None:
        response = self.client.post(
            "/api/vehicles/",
            {"registration": "VEH-001", "vehicle_type": VehicleType.CAR},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("registration", response.data)
        self.assertEqual(Vehicle.objects.count(), 1)

    def test_create_vehicle_rejects_invalid_vehicle_type_or_unknown_customer(self) -> None:
        invalid_type = self.client.post(
            "/api/vehicles/",
            {"registration": "VEH-004", "vehicle_type": "truck"},
            format="json",
        )
        self.assertEqual(invalid_type.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("vehicle_type", invalid_type.data)

        unknown_customer = self.client.post(
            "/api/vehicles/",
            {"registration": "VEH-005", "vehicle_type": VehicleType.CAR, "customer": 99999},
            format="json",
        )
        self.assertEqual(unknown_customer.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("customer", unknown_customer.data)

        self.assertEqual(Vehicle.objects.count(), 1)


class VehicleReadApiTests(VehicleCrudApiTestBase):
    def test_list_and_retrieve_vehicles(self) -> None:
        other = Vehicle.objects.create(
            registration="VEH-002",
            vehicle_type=VehicleType.MOTORCYCLE,
        )

        list_response = self.client.get("/api/vehicles/")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [row["id"] for row in list_response.data],
            [self.vehicle.pk, other.pk],
        )

        retrieve_response = self.client.get(f"/api/vehicles/{other.pk}/")
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data["id"], other.pk)
        self.assertEqual(retrieve_response.data["registration"], "VEH-002")
        self.assertEqual(retrieve_response.data["vehicle_type"], VehicleType.MOTORCYCLE)
        self.assertEqual(retrieve_response.data["customer"], None)
        self.assertIn("created_at", retrieve_response.data)
        self.assertIn("updated_at", retrieve_response.data)
