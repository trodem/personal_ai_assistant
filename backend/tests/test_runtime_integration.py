import socket
import urllib.error
import urllib.request
import unittest


class RuntimeIntegrationTests(unittest.TestCase):
    def test_backend_http_endpoint_responds(self) -> None:
        try:
            with urllib.request.urlopen("http://localhost:8000", timeout=5) as response:
                self.assertEqual(response.status, 200)
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


if __name__ == "__main__":
    unittest.main()
