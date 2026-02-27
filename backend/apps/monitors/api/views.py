from datetime import datetime
from typing import Optional

from django.utils.dateparse import parse_datetime
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from apps.core.models import Project
from apps.monitors.models import Monitor, CheckResult

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MonitorViewSet(viewsets.ModelViewSet):
    serializer_class = MonitorSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Monitor.objects.filter(project__owner=self.request.user)

    def perform_create(self, serializer):
        project = serializer.validated_data["project"]
        if project.owner_id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("not your project")
        serializer.save()

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

        ser = CheckResultSerializer(qs[:500], many=True)
        return Response({
            "result": ser.data,
            "user": request.user.username,
        })
