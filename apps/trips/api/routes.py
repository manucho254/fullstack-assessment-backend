from rest_framework.routers import DefaultRouter


router = DefaultRouter()
from apps.trips.api.views import TripViewSet

router.register(r"", TripViewSet, basename="trips")