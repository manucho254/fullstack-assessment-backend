from rest_framework.serializers import ModelSerializer

from apps.drivers.models import Driver
from apps.users.api.serializers import UserSerializer


class DriverSerializer(ModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Driver
        fields = [
            "id",
            "user",
            "license_number",
            "current_location",
            "status",
            "current_cycle_hours",
            "home_terminal_time_zone",
            "created_at",
        ]
