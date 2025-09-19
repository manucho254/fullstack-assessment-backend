from rest_framework.routers import DefaultRouter


from apps.logs.api.views import HOSLogViewSet, DutyPeriodViewSet

router = DefaultRouter()

router.register(r"hos", HOSLogViewSet, basename="hoslogs")
router.register(r"hos/periods", DutyPeriodViewSet, basename="dutyperiods")
