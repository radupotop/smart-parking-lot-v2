"""Tests for the parking app."""

from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from parking.models import (
    Customer,
    LoyaltyTier,
    ParkingSpot,
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
