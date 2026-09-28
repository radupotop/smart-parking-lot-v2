"""Shared pricing constants and helpers."""

from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal, ROUND_HALF_UP

from parking.models import LoyaltyTier, PublicHoliday, VehicleType

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


@dataclass(frozen=True)
class TimeWindow:
    """A same-day clock window with configurable boundary inclusion."""

    start: time
    end: time
    include_start: bool = True
    include_end: bool = False


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
