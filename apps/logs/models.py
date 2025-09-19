from apps.utils.base import BaseModel

from django.db import models


class HOSLog(BaseModel):
    driver = models.ForeignKey(
        "drivers.Driver", on_delete=models.CASCADE, related_name="hos_logs"
    )
    trip = models.ForeignKey(
        "trips.Trip",
        on_delete=models.CASCADE,
        related_name="hos_logs",
        null=True,
        blank=True,
    )
    time_zone = models.CharField(max_length=50)
    shipping_document = models.CharField(max_length=100, null=True, blank=True)
    commodity = models.CharField(max_length=100, null=True, blank=True)
    total_drive_time = models.IntegerField(default=0)  # in minutes
    total_on_duty_time = models.IntegerField(default=0)  # in minutes
    cycle_hours_used = models.IntegerField(default=0)  # in minutes

    def __str__(self):
        return f"HOS Log for Driver {self.driver.id} on {self.created_at}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "HOS Logs"


class DutyPeriod(BaseModel):
    hos_log = models.ForeignKey(
        "HOSLog", on_delete=models.CASCADE, related_name="duty_periods"
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ("driving", "Driving"),
            ("on_duty", "On Duty"),
            ("off_duty", "Off Duty"),
            ("sleeper_berth", "Sleeper Berth"),
        ],
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)  # in minutes
    location = models.ForeignKey(
        "locations.Location", on_delete=models.SET_NULL, null=True, blank=True
    )
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Duty Period ({self.status}) for HOS Log {self.hos_log.id}"

    class Meta:
        ordering = ["-start_time"]
        verbose_name_plural = "Duty Periods"


class HOSViolation(BaseModel):
    hos_log = models.ForeignKey(
        "HOSLog", on_delete=models.CASCADE, related_name="violations"
    )
    type = models.CharField(
        max_length=50,
        choices=[
            ("daily_drive_limit", "Daily Drive Limit Exceeded"),
            ("daily_on_duty_limit", "Daily On-Duty Limit Exceeded"),
            ("cycle_limit", "Cycle Limit Exceeded"),
            ("break_required", "Break Required"),
        ],
    )
    severity = models.CharField(
        max_length=50,
        choices=[
            ("warning", "Warning"),
            ("violation", "Violation"),
        ],
        default="warning",
    )
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"HOS Violation ({self.type}) for HOS Log {self.hos_log.id}"

    class Meta:
        ordering = ["-timestamp"]
        verbose_name_plural = "HOS Violations"
