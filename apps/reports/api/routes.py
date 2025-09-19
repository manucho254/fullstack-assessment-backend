from rest_framework.routers import DefaultRouter

from apps.reports.api.views import ComplianceReportViewSet

router = DefaultRouter()
router.register(r"", ComplianceReportViewSet, basename="compliance-report")
