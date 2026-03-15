import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class ApiBackwardCompatibilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        user_id = f"user-compat-{uuid4()}"
        admin_id = f"admin-compat-{uuid4()}"
        user_token = build_dev_token(user_id, tenant_id="tenant-a")
        admin_token = build_dev_token(admin_id, tenant_id="tenant-a", role="admin", mfa_enabled=True)
        self.user_headers = {"Authorization": f"Bearer {user_token}", "x-tenant-id": "tenant-a"}
        self.admin_headers = {"Authorization": f"Bearer {admin_token}", "x-tenant-id": "tenant-a"}

    def _save_expense_memory(self) -> None:
        response = self.client.post(
            "/api/v1/memory",
            headers=self.user_headers,
            json={
                "memory_type": "expense_event",
                "raw_text": "I bought bread for 3 CHF",
                "structured_data": {"item": "bread", "amount": 3.0, "currency": "CHF"},
                "confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_only_v1_api_paths_are_published(self) -> None:
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        schema = response.json()
        api_paths = [path for path in schema["paths"].keys() if path.startswith("/api/")]
        self.assertTrue(api_paths, "No /api paths were found in OpenAPI schema.")
        self.assertTrue(all(path.startswith("/api/v1/") for path in api_paths))

    def test_memories_response_keeps_previous_supported_client_fields(self) -> None:
        self._save_expense_memory()
        response = self.client.get("/api/v1/memories", headers=self.user_headers)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["items"])
        previous_required_fields = {"id", "memory_type", "raw_text", "structured_data", "created_at"}
        self.assertTrue(previous_required_fields.issubset(set(payload["items"][0].keys())))

    def test_memories_response_supports_active_client_fields(self) -> None:
        self._save_expense_memory()
        response = self.client.get("/api/v1/memories", headers=self.user_headers)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["items"])
        active_required_fields = {
            "id",
            "memory_type",
            "raw_text",
            "structured_data",
            "structured_data_schema_version",
            "created_at",
            "ai_state",
        }
        self.assertTrue(active_required_fields.issubset(set(payload["items"][0].keys())))

    def test_question_response_keeps_previous_and_active_client_fields(self) -> None:
        self._save_expense_memory()
        response = self.client.post(
            "/api/v1/question",
            headers=self.user_headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        previous_required_fields = {"answer"}
        active_required_fields = {"answer", "confidence", "source_memory_ids"}
        self.assertTrue(previous_required_fields.issubset(set(payload.keys())))
        self.assertTrue(active_required_fields.issubset(set(payload.keys())))

    def test_user_settings_response_keeps_previous_and_active_client_fields(self) -> None:
        response = self.client.get("/api/v1/me/settings", headers=self.user_headers)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        previous_required_fields = {"user_id", "preferred_language", "role", "status", "subscription_plan"}
        active_required_fields = {
            "auth_provider",
            "mfa_enabled",
            "billing_exempt",
            "payment_methods_enabled",
            "notification_preferences",
        }
        self.assertTrue(previous_required_fields.issubset(set(payload.keys())))
        self.assertTrue(active_required_fields.issubset(set(payload.keys())))

    def test_admin_users_response_keeps_previous_and_active_client_fields(self) -> None:
        response = self.client.get("/api/v1/admin/users", headers=self.admin_headers)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["items"])
        previous_required_fields = {"id", "role"}
        active_required_fields = {"status", "subscription_plan", "billing_exempt"}
        self.assertTrue(previous_required_fields.issubset(set(payload["items"][0].keys())))
        self.assertTrue(active_required_fields.issubset(set(payload["items"][0].keys())))


if __name__ == "__main__":
    unittest.main()
