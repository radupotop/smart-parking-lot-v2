"""Admin inspection tests for the parking app."""

from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from parking.models import (
    Customer,
    LoyaltyTier,
    ParkingSpot,
    SpotTypeVehicleCompatibility,
    Vehicle,
    VehicleType,
)
from parking.services import record_entry, record_exit


class ParkingAdminInspectionTests(TestCase):
    """Verify the admin can inspect sessions and the evaluation audit trail."""

    def setUp(self):
        self.user = User.objects.create_superuser(username="admin", password="pass")
        self.client.force_login(self.user)
        self.customer = Customer.objects.create(loyalty_tier=LoyaltyTier.GOLD)
        self.vehicle = Vehicle.objects.create(
            registration="ADMIN-1",
            vehicle_type=VehicleType.CAR,
            customer=self.customer,
        )
        self.spot = ParkingSpot.objects.create(
            level=1, number="A1", spot_type="compact"
        )
        SpotTypeVehicleCompatibility.objects.create(
            spot_type="compact", vehicle_type=VehicleType.CAR
        )
        entered_at = timezone.now() - timedelta(hours=1)
        self.session = record_entry(
            vehicle=self.vehicle,
            spot=self.spot,
            customer=self.customer,
            entered_at=entered_at,
        )
        self.session = record_exit(self.session)

    def test_session_list_page_renders(self):
        response = self.client.get(
            reverse("admin:parking_parkingsession_changelist")
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ADMIN-1")

    def test_session_change_page_shows_selected_evaluation_and_audit_trail(self):
        response = self.client.get(
            reverse("admin:parking_parkingsession_change", args=[self.session.pk])
        )
        self.assertEqual(response.status_code, 200)
        # Charged amount from the selected evaluation is visible.
        self.assertContains(response, str(self.session.charged_amount))
        # The per-policy audit trail inline lists every evaluated policy.
        self.assertContains(response, "Standard")
        self.assertContains(response, "Early Bird")
        self.assertContains(response, "Night Owl")

    def test_rate_evaluation_list_page_renders(self):
        response = self.client.get(
            reverse("admin:parking_rateevaluation_changelist")
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ADMIN-1")
