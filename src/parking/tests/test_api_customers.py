"""API tests for the /api/customers/ endpoint (full CRUD)."""

from rest_framework import status
from rest_framework.test import APITestCase

from parking.models import Customer, LoyaltyTier


class CustomerCrudApiTestBase(APITestCase):
    """Shared fixture: one persisted customer."""

    def setUp(self) -> None:
        self.customer = Customer.objects.create(loyalty_tier=LoyaltyTier.SILVER)


class CustomerCreateApiTests(CustomerCrudApiTestBase):
    def test_create_customer_returns_created_representation(self) -> None:
        response = self.client.post(
            "/api/customers/",
            {"loyalty_tier": LoyaltyTier.GOLD},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["loyalty_tier"], LoyaltyTier.GOLD)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

        created = Customer.objects.get(pk=response.data["id"])
        self.assertEqual(created.loyalty_tier, LoyaltyTier.GOLD)
        self.assertEqual(Customer.objects.count(), 2)

    def test_create_customer_rejects_invalid_loyalty_tier(self) -> None:
        response = self.client.post(
            "/api/customers/",
            {"loyalty_tier": "diamond"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("loyalty_tier", response.data)
        self.assertEqual(Customer.objects.count(), 1)


class CustomerReadApiTests(CustomerCrudApiTestBase):
    def test_list_and_retrieve_customers(self) -> None:
        other = Customer.objects.create(loyalty_tier=LoyaltyTier.PLATINUM)

        list_response = self.client.get("/api/customers/")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [row["id"] for row in list_response.data],
            [self.customer.pk, other.pk],
        )

        retrieve_response = self.client.get(f"/api/customers/{other.pk}/")
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data["id"], other.pk)
        self.assertEqual(retrieve_response.data["loyalty_tier"], LoyaltyTier.PLATINUM)
        self.assertIn("created_at", retrieve_response.data)
        self.assertIn("updated_at", retrieve_response.data)


class CustomerUpdateApiTests(CustomerCrudApiTestBase):
    def test_update_customer(self) -> None:
        response = self.client.patch(
            f"/api/customers/{self.customer.pk}/",
            {"loyalty_tier": LoyaltyTier.GOLD},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["loyalty_tier"], LoyaltyTier.GOLD)

        self.customer.refresh_from_db()
        self.assertEqual(self.customer.loyalty_tier, LoyaltyTier.GOLD)


class CustomerDeleteApiTests(CustomerCrudApiTestBase):
    def test_delete_customer(self) -> None:
        response = self.client.delete(f"/api/customers/{self.customer.pk}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Customer.objects.count(), 0)
