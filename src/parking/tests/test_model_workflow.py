"""Workflow persistence tests for the entry/exit ticket model.

These DB-backed tests close the remaining gaps for TASK-5.3 acceptance
criteria 4 and 5: the exit workflow must close the session and persist the
cheapest *applicable* evaluation as the selected charge, and it must persist
exactly one ``RateEvaluation`` per considered policy with correct flags,
amounts, and non-empty audit details (without duplicating rows on re-exit).

Acceptance criteria 1-3 (unique constraints, loyalty tier snapshot on entry,
incompatible spot rejection) are already fully covered by
``tests.ParkingFoundationModelTests`` and
``tests.test_services.RecordEntryServiceTests`` and are intentionally not
duplicated here.
"""

from datetime import datetime, timezone
from decimal import Decimal

from django.test import TestCase

from parking.models import (
    Customer,
    LoyaltyTier,
    ParkingSpot,
    RateEvaluation,
    RatePolicy,
    SessionStatus,
    SpotType,
    SpotTypeVehicleCompatibility,
    Vehicle,
    VehicleType,
)
from parking.services import record_entry, record_exit


class ModelWorkflowTestBase(TestCase):
    """Shared fixtures: a gold customer, a car, and a compatible compact spot."""

    def setUp(self) -> None:
        self.customer = Customer.objects.create(loyalty_tier=LoyaltyTier.GOLD)
        self.vehicle = Vehicle.objects.create(
            registration="MWF-001",
            vehicle_type=VehicleType.CAR,
            customer=self.customer,
        )
        self.spot = ParkingSpot.objects.create(
            level=1,
            number="MWF-01",
            spot_type=SpotType.COMPACT,
        )
        SpotTypeVehicleCompatibility.objects.get_or_create(
            spot_type=SpotType.COMPACT,
            vehicle_type=VehicleType.CAR,
        )


class ExitWorkflowSelectionTests(ModelWorkflowTestBase):
    """AC 4: exit closes the session and selects the cheapest applicable policy."""

    def test_exit_workflow_closes_session_and_selects_cheapest_applicable_evaluation(self) -> None:
        # Monday 2026-09-28 06:00 -> 16:00: both Standard Hourly ($27.50 with
        # peak surcharges) and Early Bird ($15.00 base, 20% gold discount ->
        # $12.00) are applicable; Night Owl is not (exit is not the next day).
        entered_at = datetime(2026, 9, 28, 6, 0, tzinfo=timezone.utc)
        exited_at = datetime(2026, 9, 28, 16, 0, tzinfo=timezone.utc)
        session = record_entry(
            self.vehicle,
            self.spot,
            customer=self.customer,
            entered_at=entered_at,
        )

        record_exit(session, exited_at=exited_at)

        session.refresh_from_db()
        self.assertEqual(session.status, SessionStatus.CLOSED)
        self.assertEqual(session.exited_at, exited_at)

        evaluations = {
            evaluation.policy: evaluation
            for evaluation in RateEvaluation.objects.filter(session=session)
        }
        self.assertTrue(evaluations[RatePolicy.STANDARD].applicable)
        self.assertEqual(evaluations[RatePolicy.STANDARD].amount, Decimal("27.50"))
        self.assertTrue(evaluations[RatePolicy.EARLY_BIRD].applicable)
        self.assertEqual(evaluations[RatePolicy.EARLY_BIRD].amount, Decimal("12.00"))

        # The selected evaluation must be the cheapest applicable one, not the
        # first configured policy.
        self.assertIsNotNone(session.selected_evaluation)
        self.assertEqual(session.selected_evaluation, evaluations[RatePolicy.EARLY_BIRD])
        self.assertEqual(session.selected_evaluation.policy, RatePolicy.EARLY_BIRD)
        self.assertEqual(session.charged_amount, Decimal("12.00"))
        self.assertLess(session.charged_amount, evaluations[RatePolicy.STANDARD].amount)

    def test_exit_workflow_selects_night_owl_when_it_is_cheapest_applicable(self) -> None:
        # Monday 2026-09-28 18:30 -> Tuesday 08:00: Night Owl ($8.00) and the
        # peak-heavy Standard Hourly policy are both applicable; Early Bird is
        # not (not the same calendar day).
        entered_at = datetime(2026, 9, 28, 18, 30, tzinfo=timezone.utc)
        exited_at = datetime(2026, 9, 29, 8, 0, tzinfo=timezone.utc)
        session = record_entry(
            self.vehicle,
            self.spot,
            customer=self.customer,
            entered_at=entered_at,
        )

        record_exit(session, exited_at=exited_at)

        session.refresh_from_db()
        evaluations = {
            evaluation.policy: evaluation
            for evaluation in RateEvaluation.objects.filter(session=session)
        }
        self.assertTrue(evaluations[RatePolicy.STANDARD].applicable)
        self.assertFalse(evaluations[RatePolicy.EARLY_BIRD].applicable)
        self.assertTrue(evaluations[RatePolicy.NIGHT_OWL].applicable)
        # Gold discount: 8.00 * 0.80 = 6.40.
        self.assertEqual(evaluations[RatePolicy.NIGHT_OWL].amount, Decimal("6.40"))
        self.assertGreater(evaluations[RatePolicy.STANDARD].amount, Decimal("6.40"))

        self.assertEqual(session.status, SessionStatus.CLOSED)
        self.assertEqual(session.selected_evaluation, evaluations[RatePolicy.NIGHT_OWL])
        self.assertEqual(session.charged_amount, Decimal("6.40"))


class ExitWorkflowAuditPersistenceTests(ModelWorkflowTestBase):
    """AC 5: one RateEvaluation per policy with flags, amounts, and details."""

    def test_exit_persists_one_rate_evaluation_per_policy_with_flags_amounts_and_details(self) -> None:
        # Monday 2026-09-28 06:00 -> 16:00 for a gold customer: standard
        # ($27.50) and early bird ($12.00) applicable, night owl rejected.
        entered_at = datetime(2026, 9, 28, 6, 0, tzinfo=timezone.utc)
        exited_at = datetime(2026, 9, 28, 16, 0, tzinfo=timezone.utc)
        session = record_entry(
            self.vehicle,
            self.spot,
            customer=self.customer,
            entered_at=entered_at,
        )

        record_exit(session, exited_at=exited_at)

        evaluations = {
            evaluation.policy: evaluation
            for evaluation in RateEvaluation.objects.filter(session=session)
        }
        self.assertEqual(len(evaluations), 3)
        self.assertEqual(
            set(evaluations),
            {RatePolicy.STANDARD, RatePolicy.EARLY_BIRD, RatePolicy.NIGHT_OWL},
        )

        # Expected applicable flags and amounts per policy.
        self.assertTrue(evaluations[RatePolicy.STANDARD].applicable)
        self.assertEqual(evaluations[RatePolicy.STANDARD].amount, Decimal("27.50"))
        self.assertTrue(evaluations[RatePolicy.EARLY_BIRD].applicable)
        self.assertEqual(evaluations[RatePolicy.EARLY_BIRD].amount, Decimal("12.00"))
        self.assertFalse(evaluations[RatePolicy.NIGHT_OWL].applicable)
        self.assertIsNone(evaluations[RatePolicy.NIGHT_OWL].amount)

        # Every evaluation carries a non-empty JSON audit trail.
        for policy, evaluation in evaluations.items():
            with self.subTest(policy=policy):
                self.assertIsInstance(evaluation.details, dict)
                self.assertGreater(len(evaluation.details), 0)
        self.assertEqual(
            evaluations[RatePolicy.NIGHT_OWL].details.get("reason"),
            "not_next_consecutive_calendar_day",
        )

        # Re-running exit is an idempotent no-op: no duplicate evaluation rows.
        first_evaluation_ids = {evaluation.pk for evaluation in evaluations.values()}
        record_exit(session, exited_at=exited_at)

        session.refresh_from_db()
        self.assertEqual(session.status, SessionStatus.CLOSED)
        self.assertEqual(session.exited_at, exited_at)
        self.assertEqual(session.charged_amount, Decimal("12.00"))
        remaining = list(RateEvaluation.objects.filter(session=session))
        self.assertEqual(len(remaining), 3)
        self.assertEqual(
            {evaluation.pk for evaluation in remaining},
            first_evaluation_ids,
        )
