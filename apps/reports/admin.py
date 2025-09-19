from django.contrib import admin

from apps.reports.models import ComplianceReport


@admin.register(ComplianceReport)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "driver",
        "vehicle",
        "period_start",
        "period_end",
        "total_violations",
    )
    search_fields = ("driver__name", "vehicle__license_plate")
    list_filter = ("period_start", "period_end")
