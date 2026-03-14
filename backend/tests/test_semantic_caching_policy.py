import unittest
from pathlib import Path
import sys
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app
from app.services.semantic_cache import (
    DEFAULT_TTL_HOURS,
    VOLATILE_TTL_HOURS,
    get_user_cache_size,
    invalidate_user_cache,
)


class SemanticCachingPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.user_id = f"user-semantic-cache-{uuid4()}"
        self.tenant_id = "tenant-a"
        self.token = build_dev_token(self.user_id, tenant_id=self.tenant_id)
        self.headers = {"Authorization": f"Bearer {self.token}", "x-tenant-id": self.tenant_id}
        invalidate_user_cache(self.tenant_id, self.user_id)

    def _save_expense(self, amount: float, currency: str = "CHF") -> None:
        response = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "expense_event",
                "raw_text": f"I spent {amount} {currency}",
                "structured_data": {"item": "expense", "amount": amount, "currency": currency},
                "confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_cache_is_user_scoped_and_populated_on_high_confidence(self) -> None:
        self._save_expense(12.0, "CHF")
        first = self.client.post("/api/v1/question", headers=self.headers, json={"question": "How much did I spend?"})
        self.assertEqual(first.status_code, 200)
        self.assertEqual(get_user_cache_size(self.tenant_id, self.user_id), 1)

        second = self.client.post(
            "/api/v1/question", headers=self.headers, json={"question": "How much did I spend ?"}
        )
        self.assertEqual(second.status_code, 200)
        self.assertEqual(get_user_cache_size(self.tenant_id, self.user_id), 1)

    def test_low_confidence_and_ambiguous_queries_bypass_cache(self) -> None:
        no_result = self.client.post("/api/v1/question", headers=self.headers, json={"question": "How much did I spend?"})
        self.assertEqual(no_result.status_code, 200)
        self.assertEqual(get_user_cache_size(self.tenant_id, self.user_id), 0)

        ambiguous = self.client.post("/api/v1/question", headers=self.headers, json={"question": "What was my last?"})
        self.assertEqual(ambiguous.status_code, 422)
        self.assertEqual(get_user_cache_size(self.tenant_id, self.user_id), 0)

    def test_memory_create_invalidates_user_cache(self) -> None:
        self._save_expense(10.0, "CHF")
        ask = self.client.post("/api/v1/question", headers=self.headers, json={"question": "How much did I spend?"})
        self.assertEqual(ask.status_code, 200)
        self.assertEqual(get_user_cache_size(self.tenant_id, self.user_id), 1)

        self._save_expense(5.0, "CHF")
        self.assertEqual(get_user_cache_size(self.tenant_id, self.user_id), 0)

    def test_volatile_and_default_ttl_constants_are_policy_aligned(self) -> None:
        self.assertEqual(DEFAULT_TTL_HOURS, 24)
        self.assertEqual(VOLATILE_TTL_HOURS, 1)


if __name__ == "__main__":
    unittest.main()
