from rest_framework.serializers import ModelSerializer

from apps.drivers.api.serializers import DriverSerializer
from apps.locations.api.serializers import LocationSerializer
from apps.vehicles.models import Vehicle, VehicleLocation


class VehicleSerializer(ModelSerializer):
    current_driver = DriverSerializer(many=False, read_only=True)
    last_known_location = LocationSerializer(many=False, read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "vehicle_number",
            "make_model",
            "current_driver",
            "last_known_location",
            "fuel_level",
            "odometer",
            "status",
        ]


class VehicleLocationSerializer(ModelSerializer):
    vehicle = VehicleSerializer(many=False, read_only=True)

    class Meta:
        model = VehicleLocation
        fields = [
            "id",
            "vehicle",
            "latitude",
            "longitude",
            "heading",
            "speed",
            "timestamp",
        ]
