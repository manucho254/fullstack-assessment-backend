from django.contrib import admin

from apps.trips.models import Trip, RouteWaypoint


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("id", "driver", "vehicle", "status", "created_at")
    search_fields = (
        "driver__user__first_name",
        "driver__user__last_name",
        "vehicle__vehicle_number",
    )
    list_filter = ("status",)
    ordering = ("-created_at",)


@admin.register(RouteWaypoint)
class RouteWaypointAdmin(admin.ModelAdmin):
    list_display = ("id", "trip", "waypoint_type", "estimated_arrival")
    search_fields = ("trip__id",)
    list_filter = ("waypoint_type",)
    ordering = ("-estimated_arrival",)
