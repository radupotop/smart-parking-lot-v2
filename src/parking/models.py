"""Parking domain models."""

from django.db import models


class VehicleType(models.TextChoices):
    """Fixed vehicle classes supported by the pricing domain."""

    MOTORCYCLE = "motorcycle", "Motorcycle"
    CAR = "car", "Car"
    BUS = "bus", "Bus"


class LoyaltyTier(models.TextChoices):
    """Customer loyalty tiers used by special-rate discounts."""

    NONE = "none", "None"
    SILVER = "silver", "Silver"
    GOLD = "gold", "Gold"
    PLATINUM = "platinum", "Platinum"


class SpotType(models.TextChoices):
    """Fixed parking spot categories."""

    COMPACT = "compact", "Compact"
    LARGE = "large", "Large"


class SessionStatus(models.TextChoices):
    """Lifecycle states for a parking ticket/session."""

    OPEN = "open", "Open"
    CLOSED = "closed", "Closed"


class RatePolicy(models.TextChoices):
    """Pricing policies evaluated for each billable session."""

    STANDARD = "standard", "Standard"
    EARLY_BIRD = "early_bird", "Early Bird"
    NIGHT_OWL = "night_owl", "Night Owl"


class Customer(models.Model):
    loyalty_tier = models.CharField(
        max_length=16,
        choices=LoyaltyTier.choices,
        default=LoyaltyTier.NONE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        identifier = self.pk if self.pk is not None else "unsaved"
        return f"Customer {identifier} ({self.get_loyalty_tier_display()})"


class Vehicle(models.Model):
    registration = models.CharField(max_length=32, unique=True)
    vehicle_type = models.CharField(max_length=16, choices=VehicleType.choices)
    customer = models.ForeignKey(
        Customer,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="vehicles",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.registration} ({self.get_vehicle_type_display()})"


class ParkingSpot(models.Model):
    level = models.PositiveSmallIntegerField()
    number = models.CharField(max_length=16)
    spot_type = models.CharField(max_length=16, choices=SpotType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["level", "number"],
                name="unique_parking_spot_level_number",
            )
        ]

    def __str__(self) -> str:
        return f"Level {self.level} Spot {self.number} ({self.get_spot_type_display()})"


class SpotTypeVehicleCompatibility(models.Model):
    spot_type = models.CharField(max_length=16, choices=SpotType.choices)
    vehicle_type = models.CharField(max_length=16, choices=VehicleType.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["spot_type", "vehicle_type"],
                name="unique_spot_type_vehicle_type",
            )
        ]

    def __str__(self) -> str:
        return f"{self.get_spot_type_display()} -> {self.get_vehicle_type_display()}"


class ParkingSession(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name="parking_sessions",
    )
    spot = models.ForeignKey(
        ParkingSpot,
        on_delete=models.PROTECT,
        related_name="parking_sessions",
    )
    customer = models.ForeignKey(
        Customer,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="parking_sessions",
    )
    entered_at = models.DateTimeField()
    exited_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=16,
        choices=SessionStatus.choices,
        default=SessionStatus.OPEN,
    )
    loyalty_tier_snapshot = models.CharField(
        max_length=16,
        choices=LoyaltyTier.choices,
        default=LoyaltyTier.NONE,
    )
    charged_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    selected_evaluation = models.ForeignKey(
        "RateEvaluation",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Session {self.pk or 'unsaved'} for {self.vehicle.registration}"


class RateEvaluation(models.Model):
    session = models.ForeignKey(
        ParkingSession,
        on_delete=models.CASCADE,
        related_name="rate_evaluations",
    )
    policy = models.CharField(max_length=32, choices=RatePolicy.choices)
    applicable = models.BooleanField(default=False)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.get_policy_display()} evaluation for session {self.session_id}"


class PublicHoliday(models.Model):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=128)

    def __str__(self) -> str:
        return f"{self.name} ({self.date})"
