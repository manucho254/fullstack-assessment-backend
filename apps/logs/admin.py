from django.contrib import admin

from apps.logs.models import HOSLog, HOSViolation, DutyPeriod


@admin.register(HOSLog)
class HOSLogAdmin(admin.ModelAdmin):
    list_display = ("id", "driver", "trip", "time_zone")
    search_fields = ("driver__user__first_name", "driver__user__last_name", "trip__id")
    list_filter = ("created_at", "time_zone")
    ordering = ("-created_at",)


@admin.register(DutyPeriod)
class DutyPeriodAdmin(admin.ModelAdmin):
    list_display = ("id", "hos_log", "status", "start_time", "end_time")
    search_fields = (
        "hos_log__driver__user__first_name",
        "hos_log__driver__user__last_name",
    )
    list_filter = ("status", "start_time")
    ordering = ("-created_at",)


@admin.register(HOSViolation)
class HOSViolationAdmin(admin.ModelAdmin):
    list_display = ("id", "hos_log", "type", "severity", "timestamp", "resolved")
    search_fields = (
        "hos_log__driver__user__first_name",
        "hos_log__driver__user__last_name",
        "type",
    )
    list_filter = ("type", "severity", "resolved", "timestamp")
    ordering = ("-timestamp",)
