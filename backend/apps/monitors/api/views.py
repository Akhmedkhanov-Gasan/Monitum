from datetime import datetime
from typing import Optional

from django.utils.dateparse import parse_datetime
from django.shortcuts import get_object_or_404

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.models import Project
from apps.monitors.models import Monitor, CheckResult
from apps.monitors.services import check_monitor

from .serializers import ProjectSerializer, MonitorSerializer, CheckResultSerializer


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        u = request.user
        if isinstance(obj, Project):
            return obj.owner_id == u.id
        if isinstance(obj, Monitor):
            return obj.project.owner_id == u.id
        if isinstance(obj, CheckResult):
            return obj.monitor.project.owner_id == u.id
        return False

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def check(self, request, pk=None):
        project = self.get_object()
        results = [
            check_monitor(monitor)
            for monitor in project.monitors.filter(is_active=True)
        ]
        ser = CheckResultSerializer(results, many=True)

        return Response(
            {
                "project_id": project.id,
                "checked": len(results),
                "results": ser.data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"])
    def status(self, request, pk=None):
        project = self.get_object()
        monitors = list(project.monitors.order_by("name"))
        active_monitors = [monitor for monitor in monitors if monitor.is_active]
        counts = {"up": 0, "down": 0, "unknown": 0}
        monitor_statuses = []

        for monitor in monitors:
            latest_result = monitor.results.order_by("-ts", "-id").first()

            if monitor.is_active:
                if latest_result and latest_result.status == "UP":
                    counts["up"] += 1
                elif latest_result and latest_result.status == "DOWN":
                    counts["down"] += 1
                else:
                    counts["unknown"] += 1

            monitor_statuses.append(
                {
                    "id": monitor.id,
                    "name": monitor.name,
                    "is_active": monitor.is_active,
                    "latest_result": (
                        CheckResultSerializer(latest_result).data
                        if latest_result
                        else None
                    ),
                }
            )

        return Response(
            {
                "project_id": project.id,
                "project_name": project.name,
                "total_monitors": len(monitors),
                "active_monitors": len(active_monitors),
                "up": counts["up"],
                "down": counts["down"],
                "unknown": counts["unknown"],
                "monitors": monitor_statuses,
            }
        )



class MonitorViewSet(viewsets.ModelViewSet):
    serializer_class = MonitorSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Monitor.objects.filter(project__owner=self.request.user)

    def perform_create(self, serializer):
        project = serializer.validated_data["project"]

        project = get_object_or_404(
            Project.objects.filter(owner=self.request.user),
            pk=project.pk,
        )

        serializer.save(project=project)

    @action(detail=True, methods=["get"])
    def results(self, request, pk=None):
        monitor = self.get_object()
        qs = monitor.results.all()

        def dt(q: Optional[str]) -> Optional[datetime]:
            return parse_datetime(q) if q else None

        dt_from = dt(request.query_params.get("from"))
        dt_to = dt(request.query_params.get("to"))

        if dt_from:
            qs = qs.filter(ts__gte=dt_from)
        if dt_to:
            qs = qs.filter(ts__lte=dt_to)

        ser = CheckResultSerializer(qs.order_by("-ts")[:500], many=True)
        return Response({
            "result": ser.data,
            "user": request.user.username,
        })

    @action(detail=True, methods=["post"])
    def check(self, request, pk=None):
        monitor = self.get_object()

        if not monitor.is_active:
            return Response(
                {"detail": "inactive monitors cannot be checked"},
                status=400,
            )

        result = check_monitor(monitor)
        ser = CheckResultSerializer(result)
        return Response(ser.data, status=201)

    @action(detail=True, methods=["get"])
    def status(self, request, pk=None):
        monitor = self.get_object()
        latest_result = monitor.results.order_by("-ts", "-id").first()

        return Response(
            {
                "monitor_id": monitor.id,
                "monitor_name": monitor.name,
                "is_active": monitor.is_active,
                "latest_result": (
                    CheckResultSerializer(latest_result).data
                    if latest_result
                    else None
                ),
            }
        )
