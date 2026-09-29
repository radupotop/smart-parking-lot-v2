"""URL configuration for the smart parking lot project."""

from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from parking import views

router = DefaultRouter()
router.register("customers", views.CustomerViewSet, basename="customer")
router.register("vehicles", views.VehicleViewSet, basename="vehicle")
router.register("spots", views.ParkingSpotViewSet, basename="parking-spot")
router.register("sessions", views.SessionViewSet, basename="session")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
