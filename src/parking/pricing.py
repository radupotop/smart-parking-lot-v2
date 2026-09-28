"""Shared pricing constants and helpers."""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from django.db import transaction

from parking.models import (
    LoyaltyTier,
    ParkingSession,
    PublicHoliday,
    RateEvaluation,
    RatePolicy,
    VehicleType,
)

CURRENCY_QUANTUM = Decimal("0.01")

VEHICLE_MULTIPLIERS = {
    VehicleType.MOTORCYCLE: Decimal("0.8"),
    VehicleType.CAR: Decimal("1.0"),
    VehicleType.BUS: Decimal("2.0"),
}

LOYALTY_DISCOUNTS = {
    LoyaltyTier.NONE: Decimal("0"),
    LoyaltyTier.SILVER: Decimal("0.10"),
    LoyaltyTier.GOLD: Decimal("0.20"),
    LoyaltyTier.PLATINUM: Decimal("0.30"),
}

STANDARD_FIRST_HOUR_RATE = Decimal("5.00")
STANDARD_SECOND_HOUR_RATE = Decimal("3.00")
STANDARD_SUBSEQUENT_HOUR_RATE = Decimal("2.00")
STANDARD_HOURLY_BASE_RATES = (
    STANDARD_FIRST_HOUR_RATE,
    STANDARD_SECOND_HOUR_RATE,
    STANDARD_SUBSEQUENT_HOUR_RATE,
)

PEAK_MULTIPLIER = Decimal("1.5")
EARLY_BIRD_RATE = Decimal("15.00")
NIGHT_OWL_RATE = Decimal("8.00")
HOUR = timedelta(hours=1)
HOUR_MICROSECONDS = int(HOUR.total_seconds() * 1_000_000)


@dataclass(frozen=True)
class TimeWindow:
    """A same-day clock window with configurable boundary inclusion."""

    start: time
    end: time
    include_start: bool = True
    include_end: bool = False


@dataclass(frozen=True)
class PolicyResult:
    policy: str
    applicable: bool
    amount: Decimal | None
    details: dict


class NoApplicableRatePolicyError(Exception):
    """Raised when every configured pricing policy rejects a session."""


PEAK_WINDOWS = (
    TimeWindow(time(7, 0), time(10, 0)),
    TimeWindow(time(16, 0), time(19, 0)),
)
EARLY_BIRD_ENTRY_WINDOW = TimeWindow(time(6, 0), time(9, 0))
EARLY_BIRD_EXIT_WINDOW = TimeWindow(time(15, 30), time(19, 0))
NIGHT_OWL_ENTRY_WINDOW = TimeWindow(time(18, 0), time.max, include_end=True)
NIGHT_OWL_EXIT_WINDOW = TimeWindow(time(5, 0), time(10, 0))


def quantize_currency(amount: Decimal) -> Decimal:
    """Round a Decimal amount to cents using half-up billing rounding."""

    return amount.quantize(CURRENCY_QUANTUM, rounding=ROUND_HALF_UP)


def contains_time(value: time, window: TimeWindow) -> bool:
    """Return whether a clock time falls inside a same-day window."""

    if window.start > window.end:
        raise ValueError("TimeWindow start must be before or equal to end")

    starts_after = value >= window.start if window.include_start else value > window.start
    ends_before = value <= window.end if window.include_end else value < window.end
    return starts_after and ends_before


def interval_overlaps(
    interval_start: datetime,
    interval_end: datetime,
    window_start: datetime,
    window_end: datetime,
) -> bool:
    """Return whether two datetime intervals overlap with exclusive ends."""

    if interval_start >= interval_end:
        raise ValueError("interval_start must be before interval_end")
    if window_start >= window_end:
        raise ValueError("window_start must be before window_end")

    return interval_start < window_end and interval_end > window_start


def window_for_date(window_date: date, window: TimeWindow, tzinfo=None) -> tuple[datetime, datetime]:
    """Build datetime boundaries for a same-day TimeWindow."""

    return (
        datetime.combine(window_date, window.start, tzinfo=tzinfo),
        datetime.combine(window_date, window.end, tzinfo=tzinfo),
    )


def is_weekday_excluding_public_holidays(value: date | datetime) -> bool:
    """Return True for Monday-Friday dates that are not configured holidays."""

    target_date = value.date() if isinstance(value, datetime) else value
    return target_date.weekday() < 5 and not PublicHoliday.objects.filter(
        date=target_date,
    ).exists()


class StandardHourlyPolicy:
    """Calculate the Standard Hourly parking policy without persisting results."""

    policy = RatePolicy.STANDARD

    def evaluate(self, session) -> PolicyResult:
        entered_at = getattr(session, "entered_at", None)
        exited_at = getattr(session, "exited_at", None)

        if entered_at is None:
            return self._not_applicable("missing_entered_at")
        if exited_at is None:
            return self._not_applicable("missing_exited_at")
        if exited_at <= entered_at:
            return self._not_applicable(
                "exited_at_must_be_after_entered_at",
                entered_at=entered_at,
                exited_at=exited_at,
            )

        try:
            vehicle_type = VehicleType(session.vehicle.vehicle_type)
        except (AttributeError, ValueError):
            return self._not_applicable("unsupported_vehicle_type")

        vehicle_multiplier = VEHICLE_MULTIPLIERS[vehicle_type]
        rounded_hours = self._rounded_hours(entered_at, exited_at)
        blocks = []
        total = Decimal("0.00")

        for index in range(rounded_hours):
            block_start = entered_at + (HOUR * index)
            block_end = block_start + HOUR
            base_rate = self._base_rate_for_hour(index + 1)
            peak = self._block_overlaps_peak(block_start, block_end)
            peak_multiplier = PEAK_MULTIPLIER if peak else Decimal("1.0")
            multiplier = vehicle_multiplier * peak_multiplier
            amount = quantize_currency(base_rate * multiplier)
            total += amount
            blocks.append(
                {
                    "number": index + 1,
                    "start": block_start.isoformat(),
                    "end": block_end.isoformat(),
                    "base_rate": str(quantize_currency(base_rate)),
                    "peak": peak,
                    "peak_multiplier": str(peak_multiplier),
                    "vehicle_multiplier": str(vehicle_multiplier),
                    "multiplier": str(multiplier),
                    "amount": str(amount),
                },
            )

        return PolicyResult(
            policy=self.policy,
            applicable=True,
            amount=quantize_currency(total),
            details={
                "rounded_hours": rounded_hours,
                "vehicle_type": vehicle_type.value,
                "vehicle_multiplier": str(vehicle_multiplier),
                "hours": blocks,
                "final_amount": str(quantize_currency(total)),
            },
        )

    def _not_applicable(self, reason: str, **context) -> PolicyResult:
        details = {"reason": reason, "hours": []}
        for key, value in context.items():
            details[key] = value.isoformat() if isinstance(value, datetime) else value
        return PolicyResult(
            policy=self.policy,
            applicable=False,
            amount=None,
            details=details,
        )

    def _rounded_hours(self, entered_at: datetime, exited_at: datetime) -> int:
        duration = exited_at - entered_at
        total_microseconds = (
            (duration.days * 24 * 60 * 60 * 1_000_000)
            + (duration.seconds * 1_000_000)
            + duration.microseconds
        )
        return (total_microseconds + HOUR_MICROSECONDS - 1) // HOUR_MICROSECONDS

    def _base_rate_for_hour(self, hour_number: int) -> Decimal:
        if hour_number == 1:
            return STANDARD_FIRST_HOUR_RATE
        if hour_number == 2:
            return STANDARD_SECOND_HOUR_RATE
        return STANDARD_SUBSEQUENT_HOUR_RATE

    def _block_overlaps_peak(self, block_start: datetime, block_end: datetime) -> bool:
        current_date = block_start.date()
        final_date = block_end.date()

        while current_date <= final_date:
            if is_weekday_excluding_public_holidays(current_date):
                for peak_window in PEAK_WINDOWS:
                    window_start, window_end = window_for_date(
                        current_date,
                        peak_window,
                        tzinfo=block_start.tzinfo,
                    )
                    if interval_overlaps(block_start, block_end, window_start, window_end):
                        return True
            current_date += timedelta(days=1)

        return False


class _SpecialFlatRatePolicy:
    """Shared calculation flow for flat-rate special policies."""

    policy: str
    base_amount: Decimal

    def evaluate(self, session) -> PolicyResult:
        details = self._base_details(session)
        validation_reason = self._populate_pricing_inputs(session, details)

        if validation_reason is not None:
            return self._not_applicable(details, validation_reason)

        entered_at = getattr(session, "entered_at")
        exited_at = getattr(session, "exited_at")
        window_reason = self._window_reason(entered_at, exited_at)

        if window_reason != "applicable":
            return self._not_applicable(details, window_reason)

        discounted_amount = self.base_amount * (Decimal("1") - details["_loyalty_discount"])
        final_amount = quantize_currency(discounted_amount * details["_vehicle_multiplier"])
        self._drop_internal_details(details)
        details.update(
            {
                "applicability_reason": "applicable",
                "reason": "applicable",
                "final_amount": str(final_amount),
            },
        )
        return PolicyResult(
            policy=self.policy,
            applicable=True,
            amount=final_amount,
            details=details,
        )

    def _base_details(self, session) -> dict:
        entered_at = getattr(session, "entered_at", None)
        exited_at = getattr(session, "exited_at", None)
        vehicle = getattr(session, "vehicle", None)
        vehicle_type = getattr(vehicle, "vehicle_type", None)
        loyalty_tier = getattr(session, "loyalty_tier_snapshot", None)

        return {
            "base_amount": str(quantize_currency(self.base_amount)),
            "loyalty_tier": loyalty_tier,
            "loyalty_discount": None,
            "vehicle_type": vehicle_type,
            "vehicle_multiplier": None,
            "entered_at": self._serialize_datetime(entered_at),
            "exited_at": self._serialize_datetime(exited_at),
            "applicability_reason": None,
            "reason": None,
            "final_amount": None,
        }

    def _populate_pricing_inputs(self, session, details: dict) -> str | None:
        entered_at = getattr(session, "entered_at", None)
        exited_at = getattr(session, "exited_at", None)

        if entered_at is None:
            return "missing_entered_at"
        if exited_at is None:
            return "missing_exited_at"
        if exited_at <= entered_at:
            return "exited_at_must_be_after_entered_at"
        if exited_at - entered_at > timedelta(hours=24):
            return "stay_longer_than_24_hours"

        try:
            vehicle_type = VehicleType(session.vehicle.vehicle_type)
        except (AttributeError, ValueError):
            return "unsupported_vehicle_type"

        details["vehicle_type"] = vehicle_type.value
        details["_vehicle_multiplier"] = VEHICLE_MULTIPLIERS[vehicle_type]
        details["vehicle_multiplier"] = str(details["_vehicle_multiplier"])

        loyalty_tier_snapshot = getattr(session, "loyalty_tier_snapshot", None)
        if loyalty_tier_snapshot is None:
            return "missing_loyalty_tier_snapshot"

        try:
            loyalty_tier = LoyaltyTier(loyalty_tier_snapshot)
        except ValueError:
            return "unsupported_loyalty_tier_snapshot"

        details["loyalty_tier"] = loyalty_tier.value
        details["_loyalty_discount"] = LOYALTY_DISCOUNTS[loyalty_tier]
        details["loyalty_discount"] = str(details["_loyalty_discount"])

        return None

    def _not_applicable(self, details: dict, reason: str) -> PolicyResult:
        self._drop_internal_details(details)
        details["applicability_reason"] = reason
        details["reason"] = reason
        details["final_amount"] = None
        return PolicyResult(
            policy=self.policy,
            applicable=False,
            amount=None,
            details=details,
        )

    def _drop_internal_details(self, details: dict) -> None:
        details.pop("_vehicle_multiplier", None)
        details.pop("_loyalty_discount", None)

    def _serialize_datetime(self, value) -> str | None:
        if isinstance(value, datetime):
            return value.isoformat()
        return None

    def _window_reason(self, entered_at: datetime, exited_at: datetime) -> str:
        raise NotImplementedError


class EarlyBirdPolicy(_SpecialFlatRatePolicy):
    """Calculate the Early Bird flat-rate special without persisting results."""

    policy = RatePolicy.EARLY_BIRD
    base_amount = EARLY_BIRD_RATE

    def _window_reason(self, entered_at: datetime, exited_at: datetime) -> str:
        if entered_at.date() != exited_at.date():
            return "not_same_calendar_day"
        if not contains_time(entered_at.time(), EARLY_BIRD_ENTRY_WINDOW):
            return "entry_time_outside_window"
        if not contains_time(exited_at.time(), EARLY_BIRD_EXIT_WINDOW):
            return "exit_time_outside_window"
        return "applicable"


class NightOwlPolicy(_SpecialFlatRatePolicy):
    """Calculate the Night Owl flat-rate special without persisting results."""

    policy = RatePolicy.NIGHT_OWL
    base_amount = NIGHT_OWL_RATE

    def _window_reason(self, entered_at: datetime, exited_at: datetime) -> str:
        if exited_at.date() != entered_at.date() + timedelta(days=1):
            return "not_next_consecutive_calendar_day"
        if not contains_time(entered_at.time(), NIGHT_OWL_ENTRY_WINDOW):
            return "entry_time_outside_window"
        if not contains_time(exited_at.time(), NIGHT_OWL_EXIT_WINDOW):
            return "exit_time_outside_window"
        return "applicable"


class ParkingRateCalculator:
    """Run configured policies and persist the selected best-value charge."""

    default_policy_classes = (
        StandardHourlyPolicy,
        EarlyBirdPolicy,
        NightOwlPolicy,
    )

    def __init__(self, policies=None) -> None:
        self.policies = list(policies) if policies is not None else [
            policy_class() for policy_class in self.default_policy_classes
        ]

    def calculate(self, session: ParkingSession) -> RateEvaluation:
        """Evaluate every configured policy and persist the cheapest applicable result."""

        results = [policy.evaluate(session) for policy in self.policies]
        selected_evaluation = None

        with transaction.atomic():
            locked_session = ParkingSession.objects.select_for_update().get(pk=session.pk)
            locked_session.selected_evaluation = None
            locked_session.charged_amount = None
            locked_session.save(update_fields=["selected_evaluation", "charged_amount"])
            RateEvaluation.objects.filter(session=locked_session).delete()

            evaluations = [
                self._create_evaluation(locked_session, result)
                for result in results
            ]
            applicable_evaluations = [
                evaluation
                for evaluation in evaluations
                if evaluation.applicable and evaluation.amount is not None
            ]

            if applicable_evaluations:
                selected_evaluation = min(
                    applicable_evaluations,
                    key=lambda evaluation: (
                        evaluation.amount,
                        self._policy_order(evaluation.policy),
                        evaluation.pk or 0,
                    ),
                )
                locked_session.selected_evaluation = selected_evaluation
                locked_session.charged_amount = selected_evaluation.amount
                locked_session.save(
                    update_fields=["selected_evaluation", "charged_amount"],
                )

        session.refresh_from_db()

        if selected_evaluation is None:
            policy_names = ", ".join(str(result.policy) for result in results) or "none"
            raise NoApplicableRatePolicyError(
                f"No applicable rate policy for session {session.pk}; "
                f"considered policies: {policy_names}",
            )

        return selected_evaluation

    def _create_evaluation(
        self,
        session: ParkingSession,
        result: PolicyResult,
    ) -> RateEvaluation:
        return RateEvaluation.objects.create(
            session=session,
            policy=result.policy,
            applicable=result.applicable,
            amount=result.amount if result.applicable else None,
            details=self._evaluation_details(result),
        )

    def _evaluation_details(self, result: PolicyResult) -> dict:
        details = self._json_compatible(result.details or {})

        if not result.applicable:
            details.setdefault("reason", "not_applicable")
            details.setdefault("applicability_reason", details["reason"])

        return details

    def _policy_order(self, policy: str) -> int:
        for index, configured_policy in enumerate(self.policies):
            if getattr(configured_policy, "policy", None) == policy:
                return index
        return len(self.policies)

    def _json_compatible(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                str(key): self._json_compatible(child_value)
                for key, child_value in value.items()
            }
        if isinstance(value, (list, tuple)):
            return [self._json_compatible(child_value) for child_value in value]
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, (date, datetime, time)):
            return value.isoformat()
        return value
