from django.contrib import admin

from apps.drivers.models import Driver


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "license_number", "status", "updated_at")
    search_fields = ("user__first_name", "user__last_name", "license_number")
    list_filter = ("status",)
    ordering = ("-created_at",)
