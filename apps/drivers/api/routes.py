from rest_framework.routers import DefaultRouter

from apps.drivers.api.views import DriverViewSet

router = DefaultRouter()

router.register(r"", DriverViewSet, basename="drivers")
