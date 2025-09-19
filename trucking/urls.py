from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from apps.users.api import routes as auth_routes
from apps.vehicles.api import routes as vehicle_routes
from apps.locations.api import routes as location_routes
from apps.trips.api import routes as trip_routes
from apps.logs.api import routes as log_routes
from apps.reports.api import routes as report_routes
from apps.drivers.api import routes as driver_routes


schema_view = get_schema_view(
    openapi.Info(
        title="DriverLog API",
        default_version="v1",
        description="Nice api documentation",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="admin@test"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

swagger_patterns = [
    path(
        "api/swagger<format>/",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "api/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
]


local_patterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include(auth_routes.router.urls)),
    path("api/drivers/", include(driver_routes.router.urls), name="driver"),
    path("api/locations/", include(location_routes.router.urls), name="location"),
    path("api/trips/", include(trip_routes.router.urls), name="trip"),
    path("api/logs/", include(log_routes.router.urls), name="log"),
    path("api/reports/", include(report_routes.router.urls), name="report"),
    path("api/vehicles/", include(vehicle_routes.router.urls), name="vehicle"),
]

urlpatterns = local_patterns + swagger_patterns

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
