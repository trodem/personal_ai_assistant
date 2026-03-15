import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class ApiContractCoreResponsesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        token = build_dev_token("user-api-contract-core", tenant_id="tenant-a")
        self.headers = {"Authorization": f"Bearer {token}", "x-tenant-id": "tenant-a"}

    def _assert_standard_error_schema(self, payload: dict) -> None:
        self.assertIn("error", payload)
        error = payload["error"]
        self.assertIn("code", error)
        self.assertIn("message", error)
        self.assertIn("details", error)
        self.assertIn("request_id", error)
        self.assertIn("retryable", error)

    def test_memory_save_success_response_contract(self) -> None:
        response = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "expense_event",
                "raw_text": "I bought milk for 2 CHF",
                "structured_data": {"item": "milk", "amount": 2.0, "currency": "CHF"},
                "confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("id", body)
        self.assertEqual(body["memory_type"], "expense_event")
        self.assertEqual(body["raw_text"], "I bought milk for 2 CHF")
        self.assertIn("structured_data", body)
        self.assertEqual(body["structured_data_schema_version"], 1)
        self.assertIn("created_at", body)
        self.assertEqual(body["ai_state"], "saved")

    def test_memory_save_returns_422_missing_required_fields_contract(self) -> None:
        response = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "expense_event",
                "raw_text": "I spent 5",
                "structured_data": {"amount": 5.0},
                "confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 422)
        body = response.json()
        self._assert_standard_error_schema(body)
        self.assertEqual(body["error"]["code"], "memory.missing_required_fields")
        self.assertIn("missing_required_fields", body["error"]["details"])

    def test_memory_save_returns_422_confirmation_required_contract(self) -> None:
        response = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "expense_event",
                "raw_text": "I bought bread for 3 CHF",
                "structured_data": {"item": "bread", "amount": 3.0, "currency": "CHF"},
                "confirmed": False,
            },
        )
        self.assertEqual(response.status_code, 422)
        body = response.json()
        self._assert_standard_error_schema(body)
        self.assertEqual(body["error"]["code"], "memory.confirmation_required")

    def test_protected_core_endpoint_returns_401_with_standard_error_contract(self) -> None:
        response = self.client.get("/api/v1/memories")
        self.assertEqual(response.status_code, 401)
        body = response.json()
        self._assert_standard_error_schema(body)
        self.assertEqual(body["error"]["code"], "auth.missing_token")


if __name__ == "__main__":
    unittest.main()
