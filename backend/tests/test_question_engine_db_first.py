import unittest
from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class QuestionEngineDatabaseFirstTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.token = build_dev_token("user-question-e2e", tenant_id="tenant-a")
        self.headers = {"Authorization": f"Bearer {self.token}", "x-tenant-id": "tenant-a"}

    def _save_expense(self, amount: float, item: str) -> None:
        response = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "expense_event",
                "raw_text": f"I bought {item} for {amount} chf",
                "structured_data": {"item": item, "amount": amount},
                "confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_question_uses_backend_aggregation_from_persisted_memories(self) -> None:
        self._save_expense(10.0, "milk")
        self._save_expense(25.5, "shoes")

        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("35.50 CHF", payload["answer"])
        self.assertEqual(payload["confidence"], "high")
        self.assertEqual(len(payload["source_memory_ids"]), 2)

    def test_question_no_result_does_not_fabricate(self) -> None:
        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "What is the weather tomorrow?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("could not find", payload["answer"].lower())
        self.assertEqual(payload["confidence"], "low")
        self.assertEqual(payload["source_memory_ids"], [])


if __name__ == "__main__":
    unittest.main()
