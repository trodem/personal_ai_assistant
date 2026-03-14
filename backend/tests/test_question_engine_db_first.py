import unittest
from pathlib import Path
import sys
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class QuestionEngineDatabaseFirstTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.token = build_dev_token(f"user-question-e2e-{uuid4()}", tenant_id="tenant-a")
        self.headers = {"Authorization": f"Bearer {self.token}", "x-tenant-id": "tenant-a"}

    def _save_expense(self, amount: float, item: str, currency: str = "CHF") -> None:
        response = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "expense_event",
                "raw_text": f"I bought {item} for {amount} chf",
                "structured_data": {"item": item, "amount": amount, "currency": currency},
                "confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_question_uses_backend_aggregation_from_persisted_memories(self) -> None:
        self._save_expense(10.0, "milk")
        self._save_expense(25.5, "shoes", "EUR")

        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("10.00 CHF", payload["answer"])
        self.assertIn("25.50 EUR", payload["answer"])
        self.assertEqual(payload["confidence"], "high")
        self.assertEqual(len(payload["source_memory_ids"]), 2)

    def test_question_out_of_scope_returns_boundary_message(self) -> None:
        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "What is the weather tomorrow?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("outside mvp scope", payload["answer"].lower())
        self.assertEqual(payload["confidence"], "low")
        self.assertEqual(payload["source_memory_ids"], [])

    def test_question_no_result_suggests_add_memory(self) -> None:
        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("add memory", payload["answer"].lower())
        self.assertEqual(payload["confidence"], "low")
        self.assertEqual(payload["source_memory_ids"], [])

    def test_latest_query_uses_latest_record_only(self) -> None:
        self._save_expense(9.0, "coffee")
        self._save_expense(19.0, "service")
        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much was my last service?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("19.00 CHF", payload["answer"])
        self.assertEqual(len(payload["source_memory_ids"]), 1)

    def test_ambiguous_last_query_returns_clarification_error(self) -> None:
        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "What was my last?"},
        )
        self.assertEqual(response.status_code, 422)
        payload = response.json()
        self.assertEqual(payload["error"]["code"], "query.ambiguous_intent")

    def test_answer_language_follows_user_preferred_language(self) -> None:
        update_profile = self.client.patch(
            "/api/v1/me/settings/profile",
            headers=self.headers,
            json={"preferred_language": "it"},
        )
        self.assertEqual(update_profile.status_code, 200)
        self._save_expense(7.0, "pane")
        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("hai speso", payload["answer"].lower())


if __name__ == "__main__":
    unittest.main()
