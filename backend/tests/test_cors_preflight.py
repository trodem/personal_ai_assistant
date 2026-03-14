import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.main import app


class CORSPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_options_preflight_succeeds_for_protected_endpoint(self) -> None:
        origin = "http://localhost:3000"
        response = self.client.options(
            "/api/v1/memories",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization,x-tenant-id",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("access-control-allow-origin"), origin)
        allow_methods = response.headers.get("access-control-allow-methods", "")
        self.assertIn("GET", allow_methods)
        self.assertTrue(response.headers.get("access-control-allow-headers"))


if __name__ == "__main__":
    unittest.main()
