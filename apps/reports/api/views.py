from django.db.models import Sum
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.reports.models import ComplianceReport
from apps.reports.api.serializers import ComplianceReportSerializer
from apps.trips.models import Trip
from apps.utils.pagination import CustomPagination
from apps.utils.base import BaseViewSet
from apps.utils.helpers import _average_driver_scores, _aggregate_violations_by_type


class ComplianceReportViewSet(BaseViewSet):
    """
    ViewSet for compliance reports and fleet/driver/trip summaries.
    """

    lookup_field = "id"
    queryset = ComplianceReport.objects.all().order_by("-period_start")
    serializer_class = ComplianceReportSerializer
    pagination_class = CustomPagination()

    @action(detail=False, methods=["get"], url_path="compliance")
    def fleet_compliance_summary(self, request):
        """
        GET /api/reports/compliance/
        → fleet compliance summary (aggregated across all drivers/vehicles).
        """
        reports = self.queryset

        summary = {
            "total_reports": reports.count(),
            "total_violations": reports.aggregate(total=Sum("total_violations"))[
                "total"
            ]
            or 0,
            "violations_by_type": _aggregate_violations_by_type(reports),
            "average_scores": _average_driver_scores(reports),
        }
        return Response(summary, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path=r"compliance/(?P<driver_id>[^/.]+)")
    def driver_compliance_report(self, request, driver_id=None):
        """
        GET /api/reports/compliance/{driver_id}/
        → compliance report(s) for a specific driver.
        """
        reports = self.queryset.filter(driver_id=driver_id)

        if not reports.exists():
            return Response(
                {"message": "No compliance reports found for this driver."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = [
            {
                "vehicle_id": report.vehicle_id,
                "period_start": report.period_start,
                "period_end": report.period_end,
                "total_violations": report.total_violations,
                "violations_by_type": report.violations_by_type,
                "driver_compliance_scores": report.driver_compliance_scores,
            }
            for report in reports
        ]
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="trips")
    def trips_report(self, request):
        """
        GET /api/reports/trips/
        → report of trips with associated compliance stats.
        """
        trips = Trip.objects.all()
        data = []

        for trip in trips:
            reports = self.queryset.filter(
                driver=trip.driver,
                vehicle=trip.vehicle,
                period_start__lte=trip.created_at,
                period_end__gte=trip.updated_at,
            )

            total_violations = sum(r.total_violations for r in reports)
            data.append(
                {
                    "trip_id": trip.id,
                    "driver_id": trip.driver_id,
                    "vehicle_id": trip.vehicle_id,
                    "status": trip.status,
                    "total_violations": total_violations,
                }
            )

        return Response(data, status=status.HTTP_200_OK)
