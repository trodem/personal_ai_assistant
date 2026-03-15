import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class QuestionSemanticRetrievalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.tenant_id = f"tenant-semantic-{uuid4()}"
        token = build_dev_token(f"user-semantic-{uuid4()}", tenant_id=self.tenant_id)
        self.headers = {"Authorization": f"Bearer {token}", "x-tenant-id": self.tenant_id}

    def _save_note(self, content: str, where: str) -> str:
        response = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "note",
                "raw_text": content,
                "structured_data": {"content": content, "what": content, "where": where},
                "confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["id"]

    def _save_expense(self, amount: float) -> None:
        response = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "expense_event",
                "raw_text": f"I spent {amount} CHF",
                "structured_data": {"item": "expense", "amount": amount, "currency": "CHF"},
                "confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_open_ended_location_query_uses_semantic_retrieval(self) -> None:
        note_id = self._save_note("Passport stored in top drawer", "top drawer")

        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "Where did I put my passport?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("top drawer", payload["answer"].lower())
        self.assertEqual(payload["source_memory_ids"], [note_id])
        self.assertIn(payload["confidence"], {"medium", "high"})

    def test_structured_query_keeps_database_first_priority_over_semantic(self) -> None:
        self._save_note("Passport stored in top drawer", "top drawer")
        self._save_expense(12.0)

        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("12.00 CHF", payload["answer"])
        self.assertEqual(payload["confidence"], "high")
        self.assertEqual(len(payload["source_memory_ids"]), 1)

    def test_structured_query_does_not_invoke_semantic_fallback(self) -> None:
        self._save_note("Passport stored in top drawer", "top drawer")
        self._save_expense(20.0)

        with patch("app.api.v1.routes.question.find_semantic_memory_match") as semantic_mock:
            response = self.client.post(
                "/api/v1/question",
                headers=self.headers,
                json={"question": "How much did I spend?"},
            )

        self.assertEqual(response.status_code, 200)
        semantic_mock.assert_not_called()
        payload = response.json()
        self.assertIn("20.00 CHF", payload["answer"])
        self.assertEqual(payload["confidence"], "high")

    def test_open_ended_query_invokes_semantic_fallback_after_no_result(self) -> None:
        note_id = self._save_note("Passport stored in top drawer", "top drawer")
        with patch(
            "app.api.v1.routes.question.find_semantic_memory_match",
            return_value={
                "memory_id": note_id,
                "raw_text": "Passport stored in top drawer",
                "structured_data": {"where": "top drawer"},
                "score": 0.91,
            },
        ) as semantic_mock:
            response = self.client.post(
                "/api/v1/question",
                headers=self.headers,
                json={"question": "Where did I put my passport?"},
            )

        self.assertEqual(response.status_code, 200)
        semantic_mock.assert_called_once()
        payload = response.json()
        self.assertEqual(payload["source_memory_ids"], [note_id])
        self.assertIn("top drawer", payload["answer"].lower())


if __name__ == "__main__":
    unittest.main()
