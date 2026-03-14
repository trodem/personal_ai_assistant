import unittest
from pathlib import Path
import sys

from fastapi.testclient import TestClient
from starlette import status

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.errors import (
    is_retryable_http_status,
    map_http_error_code,
)
from app.main import app


class ErrorModelContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_http_status_to_error_code_mapping_matches_contract(self) -> None:
        self.assertEqual(map_http_error_code(status.HTTP_400_BAD_REQUEST), "memory.validation_failed")
        self.assertEqual(map_http_error_code(status.HTTP_401_UNAUTHORIZED), "auth.invalid_token")
        self.assertEqual(map_http_error_code(status.HTTP_403_FORBIDDEN), "auth.forbidden")
        self.assertEqual(map_http_error_code(status.HTTP_404_NOT_FOUND), "memory.not_found")
        self.assertEqual(
            map_http_error_code(status.HTTP_422_UNPROCESSABLE_ENTITY),
            "memory.missing_required_fields",
        )
        self.assertEqual(map_http_error_code(status.HTTP_429_TOO_MANY_REQUESTS), "rate.limit_exceeded")
        self.assertEqual(map_http_error_code(status.HTTP_503_SERVICE_UNAVAILABLE), "ai.provider_unavailable")
        self.assertEqual(map_http_error_code(status.HTTP_500_INTERNAL_SERVER_ERROR), "internal.unexpected_error")

    def test_retryable_policy_matches_contract(self) -> None:
        self.assertTrue(is_retryable_http_status(status.HTTP_429_TOO_MANY_REQUESTS))
        self.assertTrue(is_retryable_http_status(status.HTTP_502_BAD_GATEWAY))
        self.assertTrue(is_retryable_http_status(status.HTTP_503_SERVICE_UNAVAILABLE))
        self.assertFalse(is_retryable_http_status(status.HTTP_400_BAD_REQUEST))
        self.assertFalse(is_retryable_http_status(status.HTTP_401_UNAUTHORIZED))
        self.assertFalse(is_retryable_http_status(status.HTTP_422_UNPROCESSABLE_ENTITY))

    def test_non_2xx_response_uses_standard_error_schema(self) -> None:
        response = self.client.get("/does-not-exist")
        self.assertEqual(response.status_code, 404)
        payload = response.json()
        self.assertIn("error", payload)
        error = payload["error"]
        self.assertIn("code", error)
        self.assertIn("message", error)
        self.assertIn("details", error)
        self.assertIn("request_id", error)
        self.assertIn("retryable", error)


if __name__ == "__main__":
    unittest.main()
