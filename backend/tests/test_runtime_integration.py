import socket
import json
import urllib.error
import urllib.request
import unittest


class RuntimeIntegrationTests(unittest.TestCase):
    def test_backend_live_health_endpoint_responds(self) -> None:
        try:
            with urllib.request.urlopen("http://localhost:8000/health/live", timeout=5) as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(response.headers.get("x-request-id") is not None, True)
                self.assertEqual(response.headers.get("x-trace-id") is not None, True)
        except urllib.error.URLError as exc:
            self.fail(f"Backend HTTP endpoint is not reachable: {exc}")

    def test_postgres_port_is_reachable(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            sock.connect(("127.0.0.1", 5432))
        except OSError as exc:
            self.fail(f"Postgres TCP port is not reachable: {exc}")
        finally:
            sock.close()

    def test_not_found_uses_standard_error_schema(self) -> None:
        request = urllib.request.Request("http://localhost:8000/does-not-exist")
        with self.assertRaises(urllib.error.HTTPError) as exc:
            urllib.request.urlopen(request, timeout=5)

        self.assertEqual(exc.exception.code, 404)
        payload = json.loads(exc.exception.read().decode("utf-8"))
        self.assertIn("error", payload)
        self.assertEqual(payload["error"]["code"], "http.not_found")
        self.assertIn("request_id", payload["error"])
        self.assertIn("retryable", payload["error"])

    def test_metrics_endpoint_exposes_counters(self) -> None:
        with urllib.request.urlopen("http://localhost:8000/metrics", timeout=5) as response:
            text = response.read().decode("utf-8")
            self.assertEqual(response.status, 200)
            self.assertIn("app_requests_total", text)
            self.assertIn("app_request_errors_total", text)
            self.assertIn("llmops_alert_threshold", text)


if __name__ == "__main__":
    unittest.main()
