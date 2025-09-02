from django.db import models
from apps.core.models import Project


class Monitor(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="monitors"
    )
    name = models.CharField(max_length=120)
    url = models.URLField()
    method = models.CharField(max_length=8, default="GET")
    expected_code = models.PositiveSmallIntegerField(default=200)
    timeout_s = models.PositiveSmallIntegerField(default=10)
    interval_s = models.PositiveSmallIntegerField(default=60)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("project", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.project}:{self.name}"

class CheckResult(models.Model):
    monitor = models.ForeignKey(
        Monitor, on_delete=models.CASCADE, related_name="results"
    )
    ts = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=8)  # UP/DOWN
    latency_ms = models.PositiveIntegerField()
    code = models.PositiveSmallIntegerField(null=True, blank=True)
    error_text = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["monitor", "-ts"])]
        ordering = ["-ts"]
