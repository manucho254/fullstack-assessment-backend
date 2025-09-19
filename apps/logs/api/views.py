from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.logs.models import HOSLog, DutyPeriod, HOSViolation
from apps.logs.api.serializers import (
    HOSLogSerializer,
    DutyPeriodSerializer,
    HOSViolationSerializer,
)
from apps.utils.pagination import CustomPagination
from apps.utils.base import BaseViewSet
from apps.logs.services import calculate_hos_status, generate_optimized_schedule
from django.db import transaction


class HOSLogViewSet(BaseViewSet):
    """
    Endpoints for managing Hours of Service (HOS) logs.
    """

    lookup_field = "log_id"
    queryset = HOSLog.objects.all().order_by("-created_at")
    serializer_class = HOSLogSerializer
    pagination_class = CustomPagination()

    def list(self, request, *args, **kwargs):
        """
        GET /api/hos/logs/ → list all logs (optionally filtered by driver).
        """
        driver_id = request.query_params.get("driver_id")
        logs = self.queryset

        if driver_id:
            logs = logs.filter(driver__id=driver_id)

        paginated_res = self.pagination_class.get_paginated_response(
            query_set=logs, serializer_obj=self.serializer_class, request=request
        )
        return Response(paginated_res, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        POST /api/hos/logs/ → create a daily log.
        """
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/hos/logs/{log_id}/ → retrieve a single log.
        """
        log = self.queryset.filter(id=kwargs.get("log_id")).first()
        if log is None:
            return Response(
                {"message": "Log not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(log)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        PUT /api/hos/logs/{log_id}/ → update a log.
        """
        log = self.queryset.filter(id=kwargs.get("log_id")).first()
        if log is None:
            return Response(
                {"message": "Log not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(log, data=request.data, partial=True)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/hos/logs/{log_id}/ → delete a log.
        """
        log = self.queryset.filter(id=kwargs.get("log_id")).first()
        if log is None:
            return Response(
                {"message": "Log not found"}, status=status.HTTP_404_NOT_FOUND
            )

        log.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get", "post"], url_path="periods")
    def periods(self, request, *args, **kwargs):
        """
        GET /api/hos/logs/{log_id}/periods/ → list duty periods
        POST /api/hos/logs/{log_id}/periods/ → add duty period
        """
        log = self.queryset.filter(id=kwargs.get("log_id")).first()
        if log is None:
            return Response(
                {"message": "Log not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if request.method == "GET":
            periods = log.dutyperiod_set.all()
            serializer = DutyPeriodSerializer(periods, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = DutyPeriodSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(hos_log=log)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"], url_path="violations")
    def violations(self, request, *args, **kwargs):
        """
        GET /api/hos/logs/{log_id}/violations/ → list violations
        POST /api/hos/logs/{log_id}/violations/ → add violation
        """
        log = self.queryset.filter(id=kwargs.get("log_id")).first()
        if log is None:
            return Response(
                {"message": "Log not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if request.method == "GET":
            violations = log.hosviolation_set.all()
            serializer = HOSViolationSerializer(violations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = HOSViolationSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(hos_log=log)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="check")
    def check(self, request, *args, **kwargs):
        """
        GET /api/hos/logs/{log_id}/check/
        → calculates HOS status and violations, saves violations in DB.
        """
        log = self.queryset.filter(id=kwargs.get("log_id")).first()
        if not log:
            return Response(
                {"message": "Log not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Build duty periods list
        periods = [
            {
                "status": dp.status,
                "start_time": dp.start_time.isoformat(),
                "end_time": dp.end_time.isoformat(),
            }
            for dp in log.dutyperiod_set.all()
        ]

        hos_result = calculate_hos_status(
            periods, getattr(log, "cycle_hours_used", 0.0)
        )

        # Save violations in DB
        with transaction.atomic():
            log.hosviolation_set.all().delete()
            for v in hos_result.get("violations", []):
                HOSViolation.objects.create(
                    hos_log=log,
                    violation_type=v["type"],
                    severity=v["severity"],
                    message=v["message"],
                    time_remaining=v.get("timeRemaining"),
                )

        return Response({"hos_status": hos_result}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="schedule")
    def schedule(self, request, *args, **kwargs):
        """
        POST /api/hos/logs/{log_id}/schedule/
        → generate + save optimized schedule as DutyPeriod records.
        Body: { "start_time": "2025-09-20T06:00:00", "total_driving_hours": 10 }
        """
        log = self.queryset.filter(id=kwargs.get("log_id")).first()
        if not log:
            return Response(
                {"message": "Log not found"}, status=status.HTTP_404_NOT_FOUND
            )

        start_time = request.data.get("start_time")
        total_driving = request.data.get("total_driving_hours")
        if not start_time or not total_driving:
            return Response(
                {"message": "start_time and total_driving_hours required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate optimized schedule
        schedule = generate_optimized_schedule(
            start_time,
            float(total_driving),
            float(getattr(log, "cycle_hours_used", 0.0)),
        )

        # Save schedule to DB as DutyPeriods
        with transaction.atomic():
            log.dutyperiod_set.all().delete()
            for block in schedule:
                DutyPeriod.objects.create(
                    hos_log=log,
                    status=block["status"],
                    start_time=block["startTime"],
                    end_time=block["endTime"],
                    remarks=block.get("remarks", ""),
                )

        return Response({"schedule": schedule}, status=status.HTTP_200_OK)


class DutyPeriodViewSet(BaseViewSet):
    """
    Endpoints for updating and deleting duty periods.
    """

    lookup_field = "duty_period_id"
    queryset = DutyPeriod.objects.all()
    serializer_class = DutyPeriodSerializer
    pagination_class = CustomPagination()

    def update(self, request, *args, **kwargs):
        """
        PUT /api/hos/periods/{duty_period_id}/ → update a duty period.
        """
        period = self.queryset.filter(id=kwargs.get("duty_period_id")).first()
        if period is None:
            return Response(
                {"message": "Duty period not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(period, data=request.data, partial=True)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/hos/periods/{duty_period_id}/ → delete a duty period.
        """
        period = self.queryset.filter(id=kwargs.get("duty_period_id")).first()
        if period is None:
            return Response(
                {"message": "Duty period not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        period.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
