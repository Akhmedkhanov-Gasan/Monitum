from time import perf_counter
from urllib import error, request

from apps.monitors.models import CheckResult, Monitor


def check_monitor(monitor: Monitor) -> CheckResult:
    started_at = perf_counter()
    req = request.Request(monitor.url, method=monitor.method.upper())

    try:
        with request.urlopen(req, timeout=monitor.timeout_s) as response:
            latency_ms = max(1, round((perf_counter() - started_at) * 1000))
            code = response.getcode()
            status = "UP" if code == monitor.expected_code else "DOWN"
            error_text = None if status == "UP" else (
                f"expected {monitor.expected_code}, got {code}"
            )
    except error.HTTPError as exc:
        latency_ms = max(1, round((perf_counter() - started_at) * 1000))
        code = exc.code
        status = "UP" if code == monitor.expected_code else "DOWN"
        error_text = None if status == "UP" else (
            f"expected {monitor.expected_code}, got {code}"
        )
    except Exception as exc:
        latency_ms = max(1, round((perf_counter() - started_at) * 1000))
        code = None
        status = "DOWN"
        error_text = str(exc)

    return CheckResult.objects.create(
        monitor=monitor,
        status=status,
        latency_ms=latency_ms,
        code=code,
        error_text=error_text,
    )
