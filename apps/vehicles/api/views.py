from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.vehicles.api.serializers import VehicleLocationSerializer, VehicleSerializer
from apps.vehicles.models import Vehicle, VehicleLocation
from apps.utils.base import BaseViewSet
from apps.utils.pagination import CustomPagination


class VehicleViewSet(BaseViewSet):
    lookup_field = "vehicle_id"
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    pagination_class = CustomPagination()

    def list(self, request, *args, **kwargs):
        """
        GET /api/vehicles/ → list all vehicles with optional search query.
        """
        query = request.query_params.get("query")
        vehicles = self.queryset

        if query:
            vehicles = vehicles.filter(
                Q(vehicle_number__icontains=query)
                | Q(make_model__icontains=query)
                | Q(current_driver__user__first_name__icontains=query)
                | Q(current_driver__user__last_name__icontains=query)
            )

        paginated_res = self.pagination_class.get_paginated_response(
            query_set=vehicles, serializer_obj=self.serializer_class, request=request
        )
        return Response(paginated_res, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        POST /api/vehicles/ → create a new vehicle.
        """
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/vehicles/{vehicle_id}/ → retrieve a specific vehicle by ID.
        """
        vehicle = self.queryset.filter(vehicle_id=kwargs.get("vehicle_id")).first()
        if vehicle is None:
            return Response(
                {"message": "Vehicle not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(vehicle)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        PUT /api/vehicles/{vehicle_id}/ → update a vehicle.
        """
        vehicle = self.queryset.filter(vehicle_id=kwargs.get("vehicle_id")).first()
        if vehicle is None:
            return Response(
                {"message": "Vehicle not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(vehicle, data=request.data, partial=True)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/vehicles/{vehicle_id}/ → delete a vehicle.
        """
        vehicle = self.queryset.filter(vehicle_id=kwargs.get("vehicle_id")).first()
        if vehicle is None:
            return Response(
                {"message": "Vehicle not found"}, status=status.HTTP_404_NOT_FOUND
            )

        vehicle.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get", "post"], url_path="locations")
    def locations(self, request, vehicle_id=None):
        """
        GET /api/vehicles/{vehicle_id}/locations/ → get location history for a vehicle.
        POST /api/vehicles/{vehicle_id}/locations/ → add a new location for a vehicle.
        """
        vehicle = self.queryset.filter(vehicle_id=vehicle_id).first()
        if vehicle is None:
            return Response(
                {"message": "Vehicle not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if request.method == "GET":
            locations = VehicleLocation.objects.filter(vehicle=vehicle).order_by(
                "-timestamp"
            )
            paginated_res = self.pagination_class.get_paginated_response(
                query_set=locations,
                serializer_obj=VehicleLocationSerializer,
                request=request,
            )
            return Response(paginated_res, status=status.HTTP_200_OK)

        # POST → add location
        data = request.data.copy()
        data["vehicle"] = vehicle.id
        serializer = VehicleLocationSerializer(data=data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
