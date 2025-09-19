from rest_framework.routers import DefaultRouter


from apps.vehicles.api.views import VehicleViewSet

router = DefaultRouter()
router.register(r"", VehicleViewSet, basename="vehicles")
