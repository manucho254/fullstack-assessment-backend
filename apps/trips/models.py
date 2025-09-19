from apps.utils.base import BaseModel

from django.db import models


class Trip(BaseModel):
    driver = models.ForeignKey(
        "drivers.Driver", on_delete=models.SET_NULL, null=True, blank=True
    )
    vehicle = models.ForeignKey(
        "vehicles.Vehicle", on_delete=models.SET_NULL, null=True, blank=True
    )
    current_location = models.ForeignKey(
        "locations.Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_location",
    )
    pickup_location = models.ForeignKey(
        "locations.Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pickup_location",
    )
    dropoff_location = models.ForeignKey(
        "locations.Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dropoff_location",
    )
    shipping_document = models.FileField(
        upload_to="shipping_documents/", null=True, blank=True
    )
    commodity = models.CharField(max_length=255, null=True, blank=True)
    current_cycle_hours = models.FloatField(default=0.0)
    status = models.CharField(
        max_length=50,
        choices=[
            ("planned", "Planned"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="planned",
    )
    time_zone = models.CharField(max_length=50, default="UTC")

    def __str__(self):
        return f"Trip {self.id} - {self.status}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Trips"


class RouteWaypoint(BaseModel):
    trip = models.ForeignKey(
        "trips.Trip", on_delete=models.CASCADE, related_name="waypoints"
    )
    waypoint_type = models.CharField(
        max_length=50,
        choices=[
            ("pickup", "Pickup"),
            ("dropoff", "Dropoff"),
            ("rest_break", "Rest Break"),
            ("fuel_stop", "Fuel Stop"),
            ("mandatory_break", "Mandatory Break"),
        ],
    )
    estimated_arrival = models.DateTimeField()
    duration_minutes = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    is_mandatory = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.waypoint_type} at {self.location} for Trip {self.trip.id}"

    class Meta:
        ordering = ["estimated_arrival"]
        verbose_name_plural = "Route Waypoints"
