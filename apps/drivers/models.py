from apps.utils.base import BaseModel

from django.db import models


class Driver(BaseModel):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)
    license_number = models.CharField(max_length=100, unique=True)
    current_location = models.ForeignKey(
        "locations.Location", on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ("available", "Available"),
            ("driving", "Driving"),
            ("on_break", "On Break"),
            ("off_duty", "Off Duty"),
        ],
        default="available",
    )
    current_cycle_hours = models.FloatField(default=0.0)
    home_terminal_time_zone = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.get_fullname} ({self.license_number})"

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Drivers"
