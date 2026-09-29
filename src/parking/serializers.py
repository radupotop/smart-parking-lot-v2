"""DRF serializers for the parking API.

Read serializers expose the full ticket state (vehicle, spot, customer,
charge, selected policy, and per-policy evaluation audit data). Write
paths are intentionally narrow: sessions are created through
``parking.services.record_entry`` and closed through
``parking.services.record_exit`` — clients can never set ``status``,
``charged_amount``, ``selected_evaluation``, or rate evaluations directly.
"""

from rest_framework import serializers

from parking.models import (
    Customer,
    ParkingSession,
    ParkingSpot,
    RateEvaluation,
    Vehicle,
)


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ("id", "loyalty_tier", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = (
            "id",
            "registration",
            "vehicle_type",
            "customer",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ParkingSpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSpot
        fields = ("id", "level", "number", "spot_type", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class RateEvaluationSerializer(serializers.ModelSerializer):
    """Read-only audit record for one policy evaluation of a session."""

    class Meta:
        model = RateEvaluation
        fields = ("id", "policy", "applicable", "amount", "details", "created_at")
        read_only_fields = fields


class SessionCreateSerializer(serializers.Serializer):
    """Input for ticket entry; validation is performed by the service."""

    vehicle = serializers.PrimaryKeyRelatedField(
        queryset=Vehicle.objects.all(),
        help_text="ID of the vehicle entering the lot.",
    )
    spot = serializers.PrimaryKeyRelatedField(
        queryset=ParkingSpot.objects.all(),
        help_text="ID of the parking spot being assigned.",
    )
    customer = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        required=False,
        allow_null=True,
        help_text=(
            "Optional customer for the ticket. Defaults to the vehicle's "
            "owner inside the entry service."
        ),
    )
    entered_at = serializers.DateTimeField(
        required=False,
        help_text="Optional ISO-8601 entry timestamp. Defaults to now.",
    )


class SessionExitSerializer(serializers.Serializer):
    """Input for ticket exit; validation is performed by the service."""

    exited_at = serializers.DateTimeField(
        required=False,
        help_text="Optional ISO-8601 exit timestamp. Defaults to now.",
    )


class SessionReadSerializer(serializers.ModelSerializer):
    """Full read representation of a ticket, including pricing audit data."""

    vehicle = VehicleSerializer(read_only=True)
    spot = ParkingSpotSerializer(read_only=True)
    customer = CustomerSerializer(read_only=True)
    selected_evaluation = RateEvaluationSerializer(read_only=True)
    rate_evaluations = RateEvaluationSerializer(many=True, read_only=True)

    class Meta:
        model = ParkingSession
        fields = (
            "id",
            "vehicle",
            "spot",
            "customer",
            "status",
            "entered_at",
            "exited_at",
            "loyalty_tier_snapshot",
            "charged_amount",
            "selected_evaluation",
            "rate_evaluations",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
