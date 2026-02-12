from rest_framework import serializers
from apps.core.models import Project
from apps.monitors.models import Monitor, CheckResult


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name"]


class MonitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitor
        fields = [
            "id",
            "project",
            "name",
            "url",
            "method",
            "expected_code",
            "timeout_s",
            "interval_s",
            "is_active",
        ]

    def validate_timeout_s(self, v):
        if not (1 <= v <= 60):
            raise serializers.ValidationError("timeout_s must be 1..60")
        return v

    def validate_interval_s(self, v):
        if not (10 <= v <= 3600):
            raise serializers.ValidationError("interval_s must be 10..3600")
        return v


class CheckResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckResult
        fields = ["id", "ts", "status", "latency_ms", "code", "error_text"]
        read_only_fields = fields

## --------------------------------------------------DEMO--------------------------------------------------
class EchoSerializer(serializers.Serializer):
    data = serializers.DictField()

    def validate_data(self, value):
        if not value.get('text'):
            raise serializers.ValidationError("No data provided")

        if len(value.get('text')) > 20:
            raise serializers.ValidationError("Text greater than 20 letters, please enter only 20 letters in it. Thanks.")
        return value
