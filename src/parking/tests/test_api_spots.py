"""API tests for the /api/spots/ endpoint (full CRUD)."""

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from parking.models import ParkingSession, ParkingSpot, SpotType, Vehicle, VehicleType


class SpotCrudApiTestBase(APITestCase):
    """Shared fixture: one persisted parking spot."""

    def setUp(self) -> None:
        self.spot = ParkingSpot.objects.create(
            level=1,
            number="A1",
            spot_type=SpotType.COMPACT,
        )


class SpotCreateApiTests(SpotCrudApiTestBase):
    def test_create_spot_returns_created_representation(self) -> None:
        response = self.client.post(
            "/api/spots/",
            {"level": 2, "number": "B1", "spot_type": SpotType.LARGE},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["level"], 2)
        self.assertEqual(response.data["number"], "B1")
        self.assertEqual(response.data["spot_type"], SpotType.LARGE)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

        created = ParkingSpot.objects.get(pk=response.data["id"])
        self.assertEqual(created.level, 2)
        self.assertEqual(created.number, "B1")
        self.assertEqual(created.spot_type, SpotType.LARGE)
        self.assertEqual(ParkingSpot.objects.count(), 2)

    def test_create_spot_rejects_duplicate_level_and_number(self) -> None:
        response = self.client.post(
            "/api/spots/",
            {"level": 1, "number": "A1", "spot_type": SpotType.LARGE},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ParkingSpot.objects.count(), 1)

    def test_create_spot_rejects_invalid_spot_type_or_missing_fields(self) -> None:
        invalid_type = self.client.post(
            "/api/spots/",
            {"level": 3, "number": "C1", "spot_type": "mega"},
            format="json",
        )
        self.assertEqual(invalid_type.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("spot_type", invalid_type.data)

        missing_fields = self.client.post(
            "/api/spots/",
            {},
            format="json",
        )
        self.assertEqual(missing_fields.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(ParkingSpot.objects.count(), 1)


class SpotReadApiTests(SpotCrudApiTestBase):
    def test_list_and_retrieve_spots(self) -> None:
        other = ParkingSpot.objects.create(
            level=2,
            number="B1",
            spot_type=SpotType.LARGE,
        )

        list_response = self.client.get("/api/spots/")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [row["id"] for row in list_response.data],
            [self.spot.pk, other.pk],
        )

        retrieve_response = self.client.get(f"/api/spots/{other.pk}/")
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data["id"], other.pk)
        self.assertEqual(retrieve_response.data["level"], 2)
        self.assertEqual(retrieve_response.data["number"], "B1")
        self.assertEqual(retrieve_response.data["spot_type"], SpotType.LARGE)
        self.assertIn("created_at", retrieve_response.data)
        self.assertIn("updated_at", retrieve_response.data)


class SpotConflictApiTests(SpotCrudApiTestBase):
    def test_update_spot_rejects_colliding_level_and_number(self) -> None:
        ParkingSpot.objects.create(
            level=2,
            number="B1",
            spot_type=SpotType.LARGE,
        )

        response = self.client.patch(
            f"/api/spots/{self.spot.pk}/",
            {"level": 2, "number": "B1"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.spot.refresh_from_db()
        self.assertEqual(self.spot.level, 1)
        self.assertEqual(self.spot.number, "A1")

    def test_delete_spot_referenced_by_session_is_rejected(self) -> None:
        vehicle = Vehicle.objects.create(
            registration="CONF-1",
            vehicle_type=VehicleType.CAR,
        )
        ParkingSession.objects.create(
            vehicle=vehicle,
            spot=self.spot,
            entered_at=timezone.now(),
        )

        response = self.client.delete(f"/api/spots/{self.spot.pk}/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(ParkingSpot.objects.filter(pk=self.spot.pk).exists())

    def test_delete_spot_without_sessions_succeeds(self) -> None:
        response = self.client.delete(f"/api/spots/{self.spot.pk}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ParkingSpot.objects.count(), 0)

    def test_create_spot_rejects_out_of_range_level_or_oversized_number(self) -> None:
        bad_level = self.client.post(
            "/api/spots/",
            {"level": -1, "number": "D1", "spot_type": SpotType.COMPACT},
            format="json",
        )
        self.assertEqual(bad_level.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("level", bad_level.data)

        bad_number = self.client.post(
            "/api/spots/",
            {"level": 4, "number": "D" + "1" * 16, "spot_type": SpotType.COMPACT},
            format="json",
        )
        self.assertEqual(bad_number.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("number", bad_number.data)

        self.assertEqual(ParkingSpot.objects.count(), 1)
