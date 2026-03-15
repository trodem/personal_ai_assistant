import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app
from app.repositories.embedding_repository import list_embeddings_for_user


class EmbeddingGenerationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.user_id = f"user-embeddings-{uuid4()}"
        self.tenant_id = "tenant-a"
        token = build_dev_token(self.user_id, tenant_id=self.tenant_id)
        self.headers = {"Authorization": f"Bearer {token}", "x-tenant-id": self.tenant_id}

    def test_generates_embedding_after_confirmed_memory_save(self) -> None:
        before = len(list_embeddings_for_user(tenant_id=self.tenant_id, user_id=self.user_id))
        response = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "expense_event",
                "raw_text": "I bought bread for 3 CHF",
                "structured_data": {"item": "bread", "amount": 3.0, "currency": "CHF"},
                "confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 200)
        saved = response.json()
        records = list_embeddings_for_user(tenant_id=self.tenant_id, user_id=self.user_id)
        self.assertEqual(len(records), before + 1)
        latest = records[-1]
        self.assertEqual(latest["memory_id"], saved["id"])
        self.assertEqual(latest["model_id"], "text-embedding-3-small")
        self.assertIsInstance(latest["embedding"], list)
        self.assertGreater(len(latest["embedding"]), 0)

    def test_does_not_generate_embedding_without_confirmation(self) -> None:
        before = len(list_embeddings_for_user(tenant_id=self.tenant_id, user_id=self.user_id))
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
        self.assertEqual(response.json()["error"]["code"], "memory.confirmation_required")
        after = len(list_embeddings_for_user(tenant_id=self.tenant_id, user_id=self.user_id))
        self.assertEqual(after, before)

    def test_idempotency_replay_does_not_duplicate_embedding(self) -> None:
        headers = dict(self.headers)
        headers["Idempotency-Key"] = "embedding-idempotency-1"
        before = len(list_embeddings_for_user(tenant_id=self.tenant_id, user_id=self.user_id))
        payload = {
            "memory_type": "expense_event",
            "raw_text": "I bought milk for 2 CHF",
            "structured_data": {"item": "milk", "amount": 2.0, "currency": "CHF"},
            "confirmed": True,
        }
        first = self.client.post("/api/v1/memory", headers=headers, json=payload)
        second = self.client.post("/api/v1/memory", headers=headers, json=payload)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.json()["id"], second.json()["id"])
        after = len(list_embeddings_for_user(tenant_id=self.tenant_id, user_id=self.user_id))
        self.assertEqual(after, before + 1)


if __name__ == "__main__":
    unittest.main()
