from rest_framework.serializers import ModelSerializer

from apps.locations.models import Location


class LocationSerializer(ModelSerializer):

    class Meta:
        model = Location
        fields = [
            "id",
            "latitude",
            "longitude",
            "address",
            "created_at",
        ]
