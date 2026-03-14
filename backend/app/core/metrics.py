from collections import defaultdict
from threading import Lock


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = Lock()
        self._request_counter: dict[tuple[str, str, int], int] = defaultdict(int)
        self._error_counter: dict[tuple[str, int], int] = defaultdict(int)

    def record_request(self, method: str, path: str, status_code: int) -> None:
        with self._lock:
            self._request_counter[(method, path, status_code)] += 1
            if status_code >= 400:
                self._error_counter[(path, status_code)] += 1

    def as_prometheus(self) -> str:
        lines: list[str] = [
            "# HELP app_requests_total Total number of processed HTTP requests.",
            "# TYPE app_requests_total counter",
        ]
        with self._lock:
            for (method, path, status_code), value in sorted(self._request_counter.items()):
                lines.append(
                    'app_requests_total{method="%s",path="%s",status="%s"} %d'
                    % (method, path, status_code, value)
                )
            lines.append("# HELP app_request_errors_total Total number of HTTP errors.")
            lines.append("# TYPE app_request_errors_total counter")
            for (path, status_code), value in sorted(self._error_counter.items()):
                lines.append(
                    'app_request_errors_total{path="%s",status="%s"} %d'
                    % (path, status_code, value)
                )
        return "\n".join(lines) + "\n"


metrics_registry = MetricsRegistry()
