"""DRF views exposing the parking ticket workflow as a REST API.

Routes (under ``/api/``):
- ``/api/customers/``, ``/api/vehicles/``, ``/api/spots/``: standard
  collection endpoints (create/list/retrieve/update/destroy).
- ``/api/sessions/``: create (ticket entry), list, retrieve.
- ``/api/sessions/<id>/exit/``: POST to record the exit and compute the
  final charge.

Error mapping:
- Serializer validation problems (missing/invalid data, unknown PKs) ->
  400 with per-field details (DRF default).
- ``IncompatibleSpotError`` (vehicle type not allowed in spot type) -> 400
  with a readable detail message.
- ``SessionExitError`` (exit on an unsaved/invalid-state session) -> 400
  with a readable detail message. Note: exiting an already-closed session
  is a documented no-op in the service and therefore succeeds with 200
  (idempotent).
- ``NoApplicableRatePolicyError`` (no pricing policy matches the stay) ->
  422 with a readable detail message; the session remains open.
"""

from django.db.models.deletion import ProtectedError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from parking.models import Customer, ParkingSession, ParkingSpot, Vehicle
from parking.pricing import NoApplicableRatePolicyError
from parking.serializers import (
    CustomerSerializer,
    ParkingSpotSerializer,
    SessionCreateSerializer,
    SessionExitSerializer,
    SessionReadSerializer,
    VehicleSerializer,
)
from parking.services import IncompatibleSpotError, SessionExitError, record_entry, record_exit


class CustomerViewSet(viewsets.ModelViewSet):
    """CRUD for customer records (loyalty tiers)."""

    queryset = Customer.objects.all().order_by("id")
    serializer_class = CustomerSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    """CRUD for vehicles."""

    queryset = Vehicle.objects.all().order_by("registration")
    serializer_class = VehicleSerializer


class ParkingSpotViewSet(viewsets.ModelViewSet):
    """CRUD for parking spots.

    Delete is overridden: the ``ParkingSession.spot`` foreign key uses
    ``on_delete=models.PROTECT``, so deleting a spot referenced by any
    session raises ``ProtectedError``. That is surfaced as a 400 with a
    readable detail message instead of a 500, and the spot is kept.
    """

    queryset = ParkingSpot.objects.all().order_by("level", "number")
    serializer_class = ParkingSpotSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.delete()
        except ProtectedError:
            return Response(
                {
                    "detail": (
                        "Cannot delete a spot that is referenced by "
                        "parking sessions."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class SessionViewSet(viewsets.ModelViewSet):
    """Ticket workflow: entry (create), list, retrieve, and exit.

    Sessions are lifecycle-managed by the application services, so they
    cannot be updated or deleted through the API (PUT/PATCH/DELETE are
    not allowed).
    """

    queryset = (
        ParkingSession.objects.select_related(
            "vehicle",
            "spot",
            "customer",
            "selected_evaluation",
        )
        .prefetch_related("rate_evaluations")
        .order_by("-entered_at", "id")
    )
    http_method_names = ["get", "post"]

    def get_serializer_class(self):
        if self.action == "create":
            return SessionCreateSerializer
        return SessionReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            session = record_entry(
                vehicle=serializer.validated_data["vehicle"],
                spot=serializer.validated_data["spot"],
                customer=serializer.validated_data.get("customer"),
                entered_at=serializer.validated_data.get("entered_at"),
            )
        except IncompatibleSpotError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            SessionReadSerializer(session).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="exit")
    def exit(self, request, pk=None):
        """Record the exit, evaluate all rate policies, and return the final charge."""

        session = self.get_object()
        exit_serializer = SessionExitSerializer(data=request.data)
        exit_serializer.is_valid(raise_exception=True)
        try:
            exited = record_exit(
                session,
                exited_at=exit_serializer.validated_data.get("exited_at"),
            )
        except SessionExitError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except NoApplicableRatePolicyError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        return Response(SessionReadSerializer(exited).data)
