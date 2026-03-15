import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class DashboardEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.user_a = f"user-dashboard-a-{uuid4()}"
        self.user_b = f"user-dashboard-b-{uuid4()}"
        token_a = build_dev_token(self.user_a, tenant_id="tenant-a")
        token_b = build_dev_token(self.user_b, tenant_id="tenant-a")
        self.headers_a = {"Authorization": f"Bearer {token_a}", "x-tenant-id": "tenant-a"}
        self.headers_b = {"Authorization": f"Bearer {token_b}", "x-tenant-id": "tenant-a"}

    def _save_memory(self, headers: dict[str, str], *, memory_type: str, raw_text: str) -> None:
        if memory_type == "note":
            structured_data = {"content": raw_text}
        elif memory_type == "expense_event":
            structured_data = {"item": "test-item", "amount": 1.0, "currency": "CHF"}
        elif memory_type == "loan_event":
            structured_data = {"person": "alice", "amount": 10.0, "currency": "CHF", "action": "lend"}
        else:
            structured_data = {"what": raw_text}
        response = self.client.post(
            "/api/v1/memory",
            headers=headers,
            json={
                "memory_type": memory_type,
                "raw_text": raw_text,
                "structured_data": structured_data,
                "confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_dashboard_returns_user_scoped_stats(self) -> None:
        self._save_memory(self.headers_a, memory_type="note", raw_text="note one")
        self._save_memory(self.headers_a, memory_type="expense_event", raw_text="expense one")
        self._save_memory(self.headers_b, memory_type="loan_event", raw_text="loan other user")

        response = self.client.get("/api/v1/dashboard", headers=self.headers_a)
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertGreaterEqual(payload["total_memories"], 2)
        self.assertIn("note", payload["memories_by_type"])
        self.assertIn("expense_event", payload["memories_by_type"])
        self.assertNotIn("loan_event", payload["memories_by_type"])
        self.assertLessEqual(len(payload["latest_memory_events"]), 5)

    def test_dashboard_requires_authentication(self) -> None:
        response = self.client.get("/api/v1/dashboard")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth.missing_token")


if __name__ == "__main__":
    unittest.main()
