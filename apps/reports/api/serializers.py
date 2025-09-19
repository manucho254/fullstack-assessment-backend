from rest_framework.serializers import ModelSerializer

from apps.reports.models import ComplianceReport
from apps.drivers.api.serializers import DriverSerializer
from apps.vehicles.api.serializers import VehicleSerializer


class ComplianceReportSerializer(ModelSerializer):
    driver = DriverSerializer(many=False, read_only=True)
    vehicle = VehicleSerializer(many=False, read_only=True)

    class Meta:
        model = ComplianceReport
        fields = [
            "id",
            "vehicle",
            "driver",
            "period_start",
            "period_end",
            "total_violations",
            "violations_by_type",
            "driver_compliance_scores",
        ]
