import unittest
from uuid import uuid4
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.core.idempotency import reset_idempotency_store
from app.main import app


class MemoryIdempotencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.user_id = f"user-idempotency-{uuid4()}"
        self.tenant_id = "tenant-a"
        self.token = build_dev_token(self.user_id, tenant_id=self.tenant_id)
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "x-tenant-id": self.tenant_id,
            "Idempotency-Key": "memory-save-1",
        }
        reset_idempotency_store()

    def _payload(self, raw_text: str = "I bought bread for 3 CHF") -> dict[str, object]:
        return {
            "memory_type": "expense_event",
            "raw_text": raw_text,
            "structured_data": {
                "item": "bread",
                "amount": 3,
                "currency": "CHF",
                "where": "shop",
                "when": "2026-03-15T00:00:00Z",
            },
            "confirmed": True,
        }

    def test_same_idempotency_key_returns_same_saved_memory(self) -> None:
        before = self.client.get("/api/v1/memories", headers=self.headers).json()["items"]

        first = self.client.post("/api/v1/memory", headers=self.headers, json=self._payload())
        second = self.client.post("/api/v1/memory", headers=self.headers, json=self._payload())
        after = self.client.get("/api/v1/memories", headers=self.headers).json()["items"]

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.json()["id"], second.json()["id"])
        self.assertEqual(first.json()["structured_data_schema_version"], 1)
        self.assertEqual(len(after), len(before) + 1)

    def test_same_key_with_different_payload_is_rejected(self) -> None:
        first = self.client.post("/api/v1/memory", headers=self.headers, json=self._payload())
        self.assertEqual(first.status_code, 200)

        second = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json=self._payload(raw_text="I bought milk for 2 CHF"),
        )
        self.assertEqual(second.status_code, 422)
        self.assertEqual(second.json()["error"]["code"], "memory.validation_failed")


if __name__ == "__main__":
    unittest.main()
