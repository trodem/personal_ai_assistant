import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class MemoryDeleteEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.user_a = f"user-delete-a-{uuid4()}"
        self.user_b = f"user-delete-b-{uuid4()}"
        token_a = build_dev_token(self.user_a, tenant_id="tenant-a")
        token_b = build_dev_token(self.user_b, tenant_id="tenant-a")
        self.headers_a = {"Authorization": f"Bearer {token_a}", "x-tenant-id": "tenant-a"}
        self.headers_b = {"Authorization": f"Bearer {token_b}", "x-tenant-id": "tenant-a"}

    def _create_memory(self, headers: dict[str, str], item: str = "bread") -> str:
        response = self.client.post(
            "/api/v1/memory",
            headers=headers,
            json={
                "memory_type": "expense_event",
                "raw_text": f"I bought {item} for 3 CHF",
                "structured_data": {"item": item, "amount": 3.0, "currency": "CHF"},
                "confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["id"]

    def test_delete_memory_soft_deletes_user_scoped_record(self) -> None:
        memory_id = self._create_memory(self.headers_a, "milk")

        delete_response = self.client.delete(f"/api/v1/memory/{memory_id}", headers=self.headers_a)
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(delete_response.json(), {"deleted": True})

        list_response = self.client.get("/api/v1/memories", headers=self.headers_a)
        self.assertEqual(list_response.status_code, 200)
        ids = [item["id"] for item in list_response.json()["items"]]
        self.assertNotIn(memory_id, ids)

    def test_delete_memory_returns_404_when_not_found(self) -> None:
        response = self.client.delete(f"/api/v1/memory/{uuid4()}", headers=self.headers_a)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "memory.not_found")

    def test_delete_memory_isolated_from_other_user(self) -> None:
        memory_id = self._create_memory(self.headers_a, "tea")
        response = self.client.delete(f"/api/v1/memory/{memory_id}", headers=self.headers_b)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "memory.not_found")


if __name__ == "__main__":
    unittest.main()
