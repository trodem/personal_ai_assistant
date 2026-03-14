import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.main import app
from app.core.auth import build_dev_token


class ErrorHandlingMiddlewareTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_error_handling_middleware_is_registered(self) -> None:
        middleware_classes = {middleware.cls.__name__ for middleware in app.user_middleware}
        self.assertIn("ErrorHandlingMiddleware", middleware_classes)

    def test_validation_error_uses_standard_code(self) -> None:
        token = build_dev_token("user-error-middleware", tenant_id=None)
        response = self.client.post(
            "/api/v1/memory",
            json={},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 422)
        payload = response.json()["error"]
        self.assertEqual(payload["code"], "memory.missing_required_fields")
        self.assertIn("request_id", payload)


if __name__ == "__main__":
    unittest.main()
