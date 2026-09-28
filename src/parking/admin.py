"""Admin registrations for the parking app."""

from django.contrib import admin

from parking.models import (
    Customer,
    ParkingSession,
    ParkingSpot,
    PublicHoliday,
    RateEvaluation,
    SpotTypeVehicleCompatibility,
    Vehicle,
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "loyalty_tier", "created_at", "updated_at")
    list_filter = ("loyalty_tier", "created_at")
    search_fields = ("vehicles__registration",)
    ordering = ("id",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "registration",
        "vehicle_type",
        "customer",
        "customer_loyalty_tier",
        "created_at",
    )
    list_filter = ("vehicle_type", "customer__loyalty_tier", "created_at")
    search_fields = ("registration",)
    ordering = ("registration",)
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Customer loyalty tier", ordering="customer__loyalty_tier")
    def customer_loyalty_tier(self, obj: Vehicle) -> str:
        return obj.customer.get_loyalty_tier_display() if obj.customer else "-"


@admin.register(ParkingSpot)
class ParkingSpotAdmin(admin.ModelAdmin):
    list_display = ("level", "number", "spot_type", "created_at")
    list_filter = ("spot_type", "level")
    search_fields = ("number",)
    ordering = ("level", "number")
    readonly_fields = ("created_at", "updated_at")


@admin.register(SpotTypeVehicleCompatibility)
class SpotTypeVehicleCompatibilityAdmin(admin.ModelAdmin):
    list_display = ("spot_type", "vehicle_type")
    list_filter = ("spot_type", "vehicle_type")
    ordering = ("spot_type", "vehicle_type")


class RateEvaluationInline(admin.TabularInline):
    model = RateEvaluation
    extra = 0
    fields = ("policy", "applicable", "amount", "details", "created_at")
    readonly_fields = fields
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None) -> bool:
        return False


@admin.register(ParkingSession)
class ParkingSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "vehicle_registration",
        "spot",
        "status",
        "entered_at",
        "exited_at",
        "loyalty_tier_snapshot",
        "charged_amount",
        "selected_evaluation",
    )
    list_filter = (
        "status",
        "loyalty_tier_snapshot",
        "entered_at",
        "exited_at",
    )
    search_fields = (
        "vehicle__registration",
        "spot__number",
        "selected_evaluation__policy",
    )
    ordering = ("-entered_at", "id")
    readonly_fields = (
        "charged_amount",
        "selected_evaluation",
        "created_at",
        "updated_at",
    )
    inlines = (RateEvaluationInline,)

    @admin.display(description="Vehicle registration", ordering="vehicle__registration")
    def vehicle_registration(self, obj: ParkingSession) -> str:
        return obj.vehicle.registration


@admin.register(RateEvaluation)
class RateEvaluationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "session",
        "vehicle_registration",
        "policy",
        "applicable",
        "amount",
        "created_at",
    )
    list_filter = ("policy", "applicable", "created_at")
    search_fields = ("session__vehicle__registration", "policy")
    ordering = ("-created_at", "id")
    readonly_fields = ("created_at",)

    @admin.display(description="Vehicle registration", ordering="session__vehicle__registration")
    def vehicle_registration(self, obj: RateEvaluation) -> str:
        return obj.session.vehicle.registration


@admin.register(PublicHoliday)
class PublicHolidayAdmin(admin.ModelAdmin):
    list_display = ("date", "name")
    list_filter = ("date",)
    search_fields = ("name",)
    ordering = ("date",)
