from urllib import error
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.core.models import Project
from apps.monitors.models import CheckResult, Monitor


class MonitorCheckApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="alice",
            password="secret123",
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        self.project = Project.objects.create(name="Main", owner=self.user)
        self.monitor = Monitor.objects.create(
            project=self.project,
            name="Homepage",
            url="https://example.com",
            method="GET",
            expected_code=200,
            timeout_s=5,
            interval_s=60,
            is_active=True,
        )

    @patch("apps.monitors.services.request.urlopen")
    def test_check_action_creates_up_result(self, mock_urlopen):
        response_obj = mock_urlopen.return_value.__enter__.return_value
        response_obj.getcode.return_value = 200

        response = self.client.post(f"/api/monitors/{self.monitor.pk}/check/")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(CheckResult.objects.count(), 1)

        result = CheckResult.objects.get()
        self.assertEqual(result.monitor, self.monitor)
        self.assertEqual(result.status, "UP")
        self.assertEqual(result.code, 200)
        self.assertIsNone(result.error_text)
        self.assertGreaterEqual(result.latency_ms, 1)

    @patch("apps.monitors.services.request.urlopen")
    def test_check_action_creates_down_result_on_timeout(self, mock_urlopen):
        mock_urlopen.side_effect = TimeoutError("timed out")

        response = self.client.post(f"/api/monitors/{self.monitor.pk}/check/")

        self.assertEqual(response.status_code, 201)
        result = CheckResult.objects.get()
        self.assertEqual(result.status, "DOWN")
        self.assertIsNone(result.code)
        self.assertEqual(result.error_text, "timed out")

    @patch("apps.monitors.services.request.urlopen")
    def test_check_action_handles_unexpected_http_code(self, mock_urlopen):
        mock_urlopen.side_effect = error.HTTPError(
            url=self.monitor.url,
            code=503,
            msg="Service Unavailable",
            hdrs=None,
            fp=None,
        )

        response = self.client.post(f"/api/monitors/{self.monitor.pk}/check/")

        self.assertEqual(response.status_code, 201)
        result = CheckResult.objects.get()
        self.assertEqual(result.status, "DOWN")
        self.assertEqual(result.code, 503)
        self.assertEqual(result.error_text, "expected 200, got 503")

    def test_check_action_rejects_inactive_monitor(self):
        self.monitor.is_active = False
        self.monitor.save(update_fields=["is_active"])

        response = self.client.post(f"/api/monitors/{self.monitor.pk}/check/")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(CheckResult.objects.count(), 0)

    def test_status_action_returns_latest_result(self):
        older_result = CheckResult.objects.create(
            monitor=self.monitor,
            status="DOWN",
            latency_ms=220,
            code=503,
            error_text="expected 200, got 503",
        )
        newer_result = CheckResult.objects.create(
            monitor=self.monitor,
            status="UP",
            latency_ms=120,
            code=200,
            error_text=None,
        )

        response = self.client.get(f"/api/monitors/{self.monitor.pk}/status/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["monitor_id"], self.monitor.pk)
        self.assertEqual(response.data["monitor_name"], self.monitor.name)
        self.assertTrue(response.data["is_active"])
        self.assertEqual(response.data["latest_result"]["id"], newer_result.pk)
        self.assertNotEqual(response.data["latest_result"]["id"], older_result.pk)
        self.assertEqual(response.data["latest_result"]["status"], "UP")

    def test_status_action_returns_null_when_no_results(self):
        response = self.client.get(f"/api/monitors/{self.monitor.pk}/status/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["monitor_id"], self.monitor.pk)
        self.assertIsNone(response.data["latest_result"])
