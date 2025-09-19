from apps.utils.base import BaseModel

from django.db import models


class Location(BaseModel):
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.address} ({self.latitude}, {self.longitude})"
