import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app
from app.services.semantic_cache import get_user_cache_size, invalidate_user_cache


class SemanticCacheOpenEndedPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.tenant_id = f"tenant-semantic-cache-{uuid4()}"
        self.user_a = f"user-sem-cache-a-{uuid4()}"
        self.user_b = f"user-sem-cache-b-{uuid4()}"

        token_a = build_dev_token(self.user_a, tenant_id=self.tenant_id)
        token_b = build_dev_token(self.user_b, tenant_id=self.tenant_id)
        self.headers_a = {"Authorization": f"Bearer {token_a}", "x-tenant-id": self.tenant_id}
        self.headers_b = {"Authorization": f"Bearer {token_b}", "x-tenant-id": self.tenant_id}

        invalidate_user_cache(self.tenant_id, self.user_a)
        invalidate_user_cache(self.tenant_id, self.user_b)

    def _save_note(self, headers: dict[str, str], content: str, where: str) -> None:
        response = self.client.post(
            "/api/v1/memory",
            headers=headers,
            json={
                "memory_type": "note",
                "raw_text": content,
                "structured_data": {"content": content, "what": content, "where": where},
                "confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_open_ended_semantic_answers_are_cached_per_user_scope(self) -> None:
        self._save_note(self.headers_a, "Passport stored in top drawer", "top drawer")
        first = self.client.post(
            "/api/v1/question",
            headers=self.headers_a,
            json={"question": "Where did I put my passport?"},
        )
        self.assertEqual(first.status_code, 200)
        self.assertEqual(get_user_cache_size(self.tenant_id, self.user_a), 1)
        self.assertEqual(get_user_cache_size(self.tenant_id, self.user_b), 0)

        second = self.client.post(
            "/api/v1/question",
            headers=self.headers_a,
            json={"question": "Where did I put my passport ?"},
        )
        self.assertEqual(second.status_code, 200)
        self.assertEqual(get_user_cache_size(self.tenant_id, self.user_a), 1)

    def test_similarity_threshold_prevents_cache_hit_for_different_open_ended_query(self) -> None:
        self._save_note(self.headers_a, "Passport stored in top drawer", "top drawer")
        first = self.client.post(
            "/api/v1/question",
            headers=self.headers_a,
            json={"question": "Where did I put my passport?"},
        )
        self.assertEqual(first.status_code, 200)
        self.assertEqual(get_user_cache_size(self.tenant_id, self.user_a), 1)
        first_answer = first.json()["answer"]

        different = self.client.post(
            "/api/v1/question",
            headers=self.headers_a,
            json={"question": "Where are my car keys now?"},
        )
        self.assertEqual(different.status_code, 200)
        self.assertNotEqual(different.json()["answer"], first_answer)
        self.assertEqual(get_user_cache_size(self.tenant_id, self.user_a), 1)


if __name__ == "__main__":
    unittest.main()
