from django.contrib import admin

from apps.vehicles.models import Vehicle, VehicleLocation


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "vehicle_number",
        "make_model",
        "status",
        "fuel_level",
        "odometer",
    )
    search_fields = ("vehicle_number", "make_model")
    list_filter = ("status",)
    ordering = ("-created_at",)


@admin.register(VehicleLocation)
class VehicleLocationAdmin(admin.ModelAdmin):
    list_display = ("id", "vehicle", "latitude", "longitude", "speed", "timestamp")
    search_fields = ("vehicle__vehicle_number",)
    ordering = ("-created_at",)
