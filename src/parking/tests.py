"""Tests for the parking app."""

from django.test import SimpleTestCase
from django.urls import reverse


class ProjectConfigurationTests(SimpleTestCase):
    """Smoke tests for the project shell."""

    def test_admin_route_is_configured(self) -> None:
        self.assertEqual(reverse("admin:index"), "/admin/")
