from rest_framework.serializers import ModelSerializer, CharField

from apps.trips.models import Trip
from apps.drivers.api.serializers import DriverSerializer
from apps.vehicles.api.serializers import VehicleSerializer
from apps.locations.api.serializers import LocationSerializer
from apps.locations.models import Location


class TripSerializer(ModelSerializer):
    driver = DriverSerializer(many=False, read_only=True)
    vehicle = VehicleSerializer(many=False, read_only=True)
    current_location = LocationSerializer(many=False, read_only=True)
    pickup_location = LocationSerializer(many=False, read_only=True)
    dropoff_location = LocationSerializer(many=False, read_only=True)

    class Meta:
        model = Trip
        fields = [
            "id",
            "driver",
            "vehicle",
            "current_location",
            "pickup_location",
            "dropoff_location",
            "shipping_document",
            "commodity",
            "current_cycle_hours",
            "status",
            "time_zone",
            "created_at",
        ]


class RouteWaypointSerializer(ModelSerializer):
    trip = TripSerializer(many=False, read_only=True)

    class Meta:
        model = Trip
        fields = [
            "id",
            "trip",
            "waypoint_type",
            "location",
            "estimated_arrival",
            "duration_minutes",
            "description",
            "is_mandatory",
            "created_at",
        ]
