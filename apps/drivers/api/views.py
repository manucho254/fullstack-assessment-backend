from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response

from apps.utils.base import BaseViewSet
from apps.utils.pagination import CustomPagination
from apps.drivers.models import Driver
from apps.drivers.api.serializers import DriverSerializer


class DriverViewSet(BaseViewSet):
    lookup_field = "driver_id"
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    pagination_class = CustomPagination()

    def list(self, request, *args, **kwargs):
        """
        List all drivers with optional query search and pagination.
        """
        query = request.query_params.get("query")
        drivers = self.queryset

        if query:
            drivers = drivers.filter(
                Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(user__email__icontains=query)
                | Q(cdl_number__icontains=query)
            )

        paginated_res = self.pagination_class.get_paginated_response(
            query_set=drivers, serializer_obj=self.serializer_class, request=request
        )
        return Response(paginated_res, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific driver profile by ID.
        """
        driver = self.queryset.filter(driver_id=kwargs.get("driver_id")).first()

        if driver is None:
            return Response(
                {"message": "Driver not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(driver)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        Update an existing driver profile.
        """
        driver = self.queryset.filter(driver_id=kwargs.get("driver_id")).first()

        if driver is None:
            return Response(
                {"message": "Driver not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(driver, data=request.data, partial=True)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a driver profile.
        """
        driver = self.queryset.filter(driver_id=kwargs.get("driver_id")).first()

        if driver is None:
            return Response(
                {"message": "Driver not found"}, status=status.HTTP_404_NOT_FOUND
            )

        driver.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
