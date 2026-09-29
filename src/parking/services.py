"""Ticket entry and exit application services.

These services implement the ticket workflow from the PRD: a ticket is issued
on entry (an open ``ParkingSession`` carrying the entry timestamp, vehicle,
spot, customer context, and a loyalty tier snapshot) and is closed on exit
when the rate calculator evaluates every configured policy and persists the
selected best-value charge.

They are plain functions so they can be reused from admin actions, API views,
and tests.
"""

from datetime import datetime

from django.db import transaction
from django.utils import timezone

from parking.models import (
    Customer,
    LoyaltyTier,
    ParkingSession,
    ParkingSpot,
    SessionStatus,
    SpotTypeVehicleCompatibility,
    Vehicle,
)
from parking.pricing import ParkingRateCalculator


class ParkingServiceError(Exception):
    """Base class for ticket workflow errors."""


class IncompatibleSpotError(ParkingServiceError):
    """Raised when the vehicle type is not allowed in the spot type."""


class SessionExitError(ParkingServiceError):
    """Raised when a session cannot be closed because required data is missing."""


def _compatibility_exists(spot_type: str, vehicle_type: str) -> bool:
    return SpotTypeVehicleCompatibility.objects.filter(
        spot_type=spot_type,
        vehicle_type=vehicle_type,
    ).exists()


def record_entry(
    vehicle: Vehicle,
    spot: ParkingSpot,
    customer: Customer | None = None,
    entered_at: datetime | None = None,
) -> ParkingSession:
    """Issue a ticket: create an open ``ParkingSession`` for the vehicle.

    - Validates that ``vehicle.vehicle_type`` is compatible with
      ``spot.spot_type`` via ``SpotTypeVehicleCompatibility`` rows and raises
      :class:`IncompatibleSpotError` for incompatible combinations.
    - ``customer`` defaults to ``vehicle.customer``; the loyalty tier snapshot
      is taken from the customer at entry time and defaults to
      ``LoyaltyTier.NONE`` when there is no customer.
    - ``entered_at`` defaults to ``timezone.now()``.
    """
    if not _compatibility_exists(spot.spot_type, vehicle.vehicle_type):
        raise IncompatibleSpotError(
            f"Vehicle type {vehicle.vehicle_type!r} is not allowed in "
            f"spot type {spot.spot_type!r}",
        )

    if customer is None:
        customer = vehicle.customer

    loyalty_tier_snapshot = (
        customer.loyalty_tier if customer is not None else LoyaltyTier.NONE
    )

    with transaction.atomic():
        return ParkingSession.objects.create(
            vehicle=vehicle,
            spot=spot,
            customer=customer,
            entered_at=entered_at or timezone.now(),
            status=SessionStatus.OPEN,
            loyalty_tier_snapshot=loyalty_tier_snapshot,
        )


def record_exit(
    session: ParkingSession,
    exited_at: datetime | None = None,
    calculator: ParkingRateCalculator | None = None,
) -> ParkingSession:
    """Close a ticket: record the exit, calculate the charge, and persist it.

    Behavior:
    - ``exited_at`` defaults to ``timezone.now()``.
    - Validates that the session is persisted, open, and has ``entered_at``,
      ``vehicle``, and ``spot``; raises :class:`SessionExitError` otherwise.
    - Calls ``ParkingRateCalculator.calculate`` (which manages its own
      transaction) to persist all policy evaluations, the selected
      evaluation, and the charged amount, then marks the session closed.
    - If the calculator raises (e.g. ``NoApplicableRatePolicyError``), the
      whole exit is rolled back and the session remains open.

    Idempotency (documented behavior): calling ``record_exit`` on a session
    that is already closed is a no-op — the refreshed session is returned
    unchanged, with no recalculation, no new evaluations, and the original
    ``exited_at`` and ``charged_amount`` preserved.
    """
    if session.pk is None:
        raise SessionExitError("Cannot exit an unsaved parking session")
    if session.status == SessionStatus.CLOSED:
        session.refresh_from_db()
        return session
    if session.status != SessionStatus.OPEN:
        raise SessionExitError(
            f"Session {session.pk} has status {session.status!r}; "
            "only open sessions can be exited",
        )
    if session.entered_at is None:
        raise SessionExitError(f"Session {session.pk} is missing entered_at")
    if session.vehicle_id is None:
        raise SessionExitError(f"Session {session.pk} is missing a vehicle")
    if session.spot_id is None:
        raise SessionExitError(f"Session {session.pk} is missing a spot")

    with transaction.atomic():
        locked_session = ParkingSession.objects.select_for_update().get(
            pk=session.pk,
        )

        locked_session.exited_at = exited_at or timezone.now()
        locked_session.save(update_fields=["exited_at"])

        (calculator or ParkingRateCalculator()).calculate(locked_session)

        locked_session.status = SessionStatus.CLOSED
        locked_session.save(update_fields=["status"])

    session.refresh_from_db()
    return session
