from rest_framework.serializers import ModelSerializer

from apps.logs.models import HOSLog, HOSViolation, DutyPeriod
from apps.trips.api.serializers import TripSerializer
from apps.drivers.api.serializers import DriverSerializer


class HOSLogSerializer(ModelSerializer):
    trip = TripSerializer(many=False, read_only=True)
    driver = DriverSerializer(many=False, read_only=False)

    class Meta:
        model = HOSLog
        fields = [
            "id",
            "driver",
            "trip",
            "time_zone",
            "shipping_document",
            "commodity",
            "total_drive_time",
            "total_on_duty_time",
            "cycle_hours_used",
            "created_at",
        ]


class DutyPeriodSerializer(ModelSerializer):
    hos_log = HOSLogSerializer(many=False, read_only=True)

    class Meta:
        model = DutyPeriod
        fields = [
            "id",
            "hos_log",
            "status",
            "start_time",
            "end_time",
            "duration_minutes",
            "location",
            "notes",
            "created_at",
        ]


class HOSViolationSerializer(ModelSerializer):
    hos_log = HOSLogSerializer(many=False, read_only=True)

    class Meta:
        model = HOSViolation
        fields = [
            "id",
            "hos_log",
            "type",
            "severity",
            "description",
            "timestamp",
            "resolved",
            "created_at",
        ]
