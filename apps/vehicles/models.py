from apps.utils.base import BaseModel

from django.db import models


class Vehicle(BaseModel):
    vehicle_number = models.CharField(max_length=100, unique=True)
    make_model = models.CharField(max_length=255)
    current_driver = models.ForeignKey(
        "drivers.Driver", on_delete=models.SET_NULL, null=True, blank=True
    )
    last_known_location = models.ForeignKey(
        "locations.Location", on_delete=models.SET_NULL, null=True, blank=True
    )
    fuel_level = models.FloatField(default=0.0)  # Percentage (0.0 to 100.0)
    odometer = models.FloatField(default=0.0)  # In miles or kilometers
    status = models.CharField(
        max_length=50,
        choices=[
            ("active", "Active"),
            ("maintenance", "Maintenance"),
            ("inactive", "Inactive"),
        ],
        default="active",
    )

    def __str__(self):
        return f"{self.vehicle_number} - {self.make_model}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Vehicles"


class VehicleLocation(BaseModel):
    """
    Model to track the real-time location of vehicles.
    """

    vehicle = models.ForeignKey("vehicles.Vehicle", on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    heading = models.FloatField(null=True, blank=True)  # In degrees
    speed = models.FloatField(null=True, blank=True)  # In miles per hour or km/h
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Location of {self.vehicle.vehicle_number} at {self.timestamp}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Vehicle Locations"
