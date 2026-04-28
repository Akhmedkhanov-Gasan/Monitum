from rest_framework import serializers
from apps.core.models import Project
from apps.monitors.models import Monitor, CheckResult


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name"]


class MonitorSerializer(serializers.ModelSerializer):
    current_status = serializers.SerializerMethodField()
    last_checked_at = serializers.SerializerMethodField()

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
            "current_status",
            "last_checked_at",
            "description",
        ]
        read_only_fields = ["current_status", "last_checked_at"]

    def get_latest_result(self, obj):
        if not hasattr(obj, "_latest_result"):
            obj._latest_result = obj.results.order_by("-ts", "-id").first()
        return obj._latest_result

    def get_current_status(self, obj):
        latest_result = self.get_latest_result(obj)
        return latest_result.status if latest_result else None

    def get_last_checked_at(self, obj):
        latest_result = self.get_latest_result(obj)
        if not latest_result:
            return None
        return serializers.DateTimeField().to_representation(latest_result.ts)

    def validate_timeout_s(self, v):
        if not (1 <= v <= 60):
            raise serializers.ValidationError("timeout_s must be 1..60")
        return v

    def validate_interval_s(self, v):
        if not (10 <= v <= 3600):
            raise serializers.ValidationError("interval_s must be 10..3600")
        return v

    def validate_name(self, name):
        if len(name) < 3:
            raise serializers.ValidationError("Name too short")
        return name

    def validate_method(self, value):
        value = value.upper()
        allowed = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
        if value not in allowed:
            raise serializers.ValidationError(
                f"method must be one of: {', '.join(sorted(allowed))}"
            )
        return value


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
