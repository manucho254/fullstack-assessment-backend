from datetime import datetime
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.drivers.models import Driver
from apps.locations.models import Location
from apps.trips.models import Trip, RouteWaypoint
from apps.trips.api.serializers import TripSerializer, RouteWaypointSerializer
from apps.utils.pagination import CustomPagination
from apps.utils.base import BaseViewSet

from apps.trips.services import (
    geocode_address,
    calculate_approx_route,
    generate_hos_waypoints,
    build_route_response,
)
from django.db import transaction
from apps.logs.services import (
    generate_optimized_schedule,
    calculate_hos_status,
    DEFAULT_LIMITS as DEFAULT_HOS_LIMITS,
)


class TripViewSet(BaseViewSet):
    lookup_field = "trip_id"
    queryset = Trip.objects.all().order_by("-created_at")
    serializer_class = TripSerializer
    pagination_class = CustomPagination()

    def list(self, request, *args, **kwargs):
        """
        GET /api/trips/ → list all trips with optional query filter.
        """
        query = request.query_params.get("query")
        trips = self.queryset

        if query:
            trips = trips.filter(
                Q(driver__name__icontains=query)
                | Q(vehicle__vehicle_number__icontains=query)
                | Q(status__icontains=query)
            )

        paginated_res = self.pagination_class.get_paginated_response(
            query_set=trips, serializer_obj=self.serializer_class, request=request
        )
        return Response(paginated_res, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        POST /api/trips/ → create a new trip.
        """
        driver = Driver.objects.filter(user=request.user).first()
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid(raise_exception=False):
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        current_location = Location.objects.create(
            address=request.data.get("current_location"), latitude=0.0, longitude=0.0
        )
        pickup_location = Location.objects.create(
            address=request.data.get("pickup_location"), latitude=0.0, longitude=0.0
        )
        dropoff_location = Location.objects.create(
            address=request.data.get("dropoff_location"), latitude=0.0, longitude=0.0
        )

        serializer.save(
            driver=driver,
            current_location=current_location,
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/trips/{trip_id}/ → retrieve a specific trip by ID.
        """
        trip = self.queryset.filter(id=kwargs.get("trip_id")).first()
        if trip is None:
            return Response(
                {"message": "Trip not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(trip)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        PUT /api/trips/{trip_id}/ → update a trip.
        """
        trip = self.queryset.filter(id=kwargs.get("trip_id")).first()
        if trip is None:
            return Response(
                {"message": "Trip not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(trip, data=request.data, partial=True)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/trips/{trip_id}/ → cancel a trip.
        """
        trip = self.queryset.filter(id=kwargs.get("trip_id")).first()
        if trip is None:
            return Response(
                {"message": "Trip not found"}, status=status.HTTP_404_NOT_FOUND
            )

        trip.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="calculate-route")
    def calculate_route(self, request, *args, **kwargs):
        """
        POST /api/trips/{trip_id}/calculate-route/
        Computes waypoints, HOS-compliant duty schedule, violations, and persists to DB.
        """
        trip = self.queryset.filter(id=kwargs.get("trip_id")).first()
        body = request.data

        try:

            def resolve(loc_key, addr_key):
                loc = body.get(loc_key)
                if (
                    loc
                    and isinstance(loc, dict)
                    and "lat" in loc
                    and ("lon" in loc or "lng" in loc)
                ):
                    return (
                        float(loc["lat"]),
                        float(loc.get("lon") or loc.get("lng")),
                    )
                addr = body.get(addr_key)
                if addr:
                    return geocode_address(addr)
                obj_loc = getattr(trip, loc_key, None)
                if obj_loc and hasattr(obj_loc, "lat"):
                    return (obj_loc.lat, obj_loc.lon)
                raise ValueError(f"No location for {loc_key}")

            origin = resolve("current_location", "current_location_address")
            pickup = resolve("pickup_location", "pickup_address")
            dropoff = resolve("dropoff_location", "dropoff_address")

        except ValueError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"message": "Geocoding failed or external service unavailable"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Routing logic
        route = calculate_approx_route([origin, pickup, dropoff])
        hos_status_input = body.get(
            "hos_status", {"drivingHoursUsed": 0.0, "canContinueDriving": True}
        )

        waypoints = generate_hos_waypoints(
            origin, pickup, dropoff, hos_status_input, route["distance"]
        )

        # Duty schedule + HOS violations

        total_driving_hours = route["duration"]
        hos_schedule = generate_optimized_schedule("06:00", total_driving_hours)
        hos_status = calculate_hos_status(hos_schedule, 0, DEFAULT_HOS_LIMITS)

        # Persist waypoints
        with transaction.atomic():
            RouteWaypoint.objects.filter(trip=trip).delete()
            for wp in waypoints:
                eta_value = wp.get("eta")
                eta_dt = None
                if eta_value:
                    try:
                        eta_dt = (
                            eta_value
                            if isinstance(eta_value, datetime)
                            else datetime.strptime(eta_value, "%H:%M")
                        )
                    except Exception:
                        eta_dt = None

                RouteWaypoint.objects.create(
                    trip=trip,
                    waypoint_type=wp.get("type"),
                    estimated_arrival=eta_dt,
                    duration_minutes=wp.get("duration_minutes", 0),
                    description=wp.get("reason") or wp.get("address") or "",
                    is_mandatory=wp.get("type") in ("rest", "mandatory_break"),
                )

        # -----------------------
        # Build frontend response
        # -----------------------
        result = {
            "route": build_route_response(
                waypoints, route["path"], route["distance"], route["duration"]
            ),
            "hosSchedule": hos_schedule,
            "hosStatus": hos_status,
        }
        
        print(result)
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get", "post"], url_path="waypoints")
    def waypoints(self, request, *args, **kwargs):
        """
        GET /api/trips/{trip_id}/waypoints/ → list waypoints for a trip
        POST /api/trips/{trip_id}/waypoints/ → add a waypoint to a trip
        """
        trip = self.queryset.filter(id=kwargs.get("trip_id")).first()
        if trip is None:
            return Response(
                {"message": "Trip not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if request.method == "GET":
            waypoints = RouteWaypoint.objects.filter(trip=trip).order_by(
                "estimated_arrival"
            )
            paginated_res = self.pagination_class.get_paginated_response(
                query_set=waypoints,
                serializer_obj=RouteWaypointSerializer,
                request=request,
            )
            return Response(paginated_res, status=status.HTTP_200_OK)

        serializer = RouteWaypointSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(trip=trip)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
