from rest_framework import status
from rest_framework.response import Response

from apps.locations.models import Location
from apps.locations.api.serializers import LocationSerializer
from apps.utils.pagination import CustomPagination
from apps.utils.base import BaseViewSet


class LocationViewSet(BaseViewSet):
    """
    Endpoints for saving and listing locations.
    """

    lookup_field = "location_id"
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    pagination_class = CustomPagination()

    def list(self, request, *args, **kwargs):
        """
        GET /api/locations/ → list saved locations
        """
        locations = self.queryset
        paginated_res = self.pagination_class.get_paginated_response(
            query_set=locations, serializer_obj=self.serializer_class, request=request
        )
        return Response(paginated_res, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        POST /api/locations/ → create a new location
        """
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
