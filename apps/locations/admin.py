from django.contrib import admin

from apps.locations.models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "address", "latitude", "longitude", "updated_at")
    search_fields = ("address",)
    ordering = ("-created_at",)
