import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.main import app


class MandatoryAuthMiddlewareTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_api_v1_requires_bearer_header(self) -> None:
        response = self.client.get("/api/v1/memories")
        self.assertEqual(response.status_code, 401)
        payload = response.json()
        self.assertEqual(payload["error"]["code"], "auth.missing_token")

    def test_api_v1_rejects_non_bearer_authorization_scheme(self) -> None:
        response = self.client.get(
            "/api/v1/memories",
            headers={"Authorization": "Basic abc123"},
        )
        self.assertEqual(response.status_code, 401)
        payload = response.json()
        self.assertEqual(payload["error"]["code"], "auth.invalid_token")

    def test_non_api_paths_are_not_forced_to_require_auth_header(self) -> None:
        response = self.client.get("/health/live")
        self.assertEqual(response.status_code, 200)

    def test_options_preflight_is_not_blocked_by_auth_middleware(self) -> None:
        response = self.client.options("/api/v1/memories")
        self.assertNotEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()

