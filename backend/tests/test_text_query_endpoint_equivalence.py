import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class TextQueryEndpointEquivalenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.tenant_id = f"tenant-text-query-{uuid4()}"
        user_token = build_dev_token(f"user-text-query-{uuid4()}", tenant_id=self.tenant_id, role="user")
        self.headers = {"Authorization": f"Bearer {user_token}", "x-tenant-id": self.tenant_id}

    def _save_expense(self, amount: float, item: str, currency: str = "CHF") -> None:
        response = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "expense_event",
                "raw_text": f"I bought {item} for {amount} {currency}",
                "structured_data": {"item": item, "amount": amount, "currency": currency},
                "confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_text_question_endpoint_returns_expected_contract(self) -> None:
        self._save_expense(10.0, "milk")
        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("answer", payload)
        self.assertIn("confidence", payload)
        self.assertIn("source_memory_ids", payload)
        self.assertEqual(payload["confidence"], "high")

    def test_text_and_voice_question_are_equivalent_for_same_prompt(self) -> None:
        self._save_expense(12.0, "bread")
        self._save_expense(8.0, "coffee")
        question = "How much did I spend?"

        text_response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": question},
        )
        self.assertEqual(text_response.status_code, 200)

        voice_response = self.client.post(
            "/api/v1/voice/question",
            headers=self.headers,
            files={"audio": ("question.wav", question.encode("utf-8"), "audio/wav")},
        )
        self.assertEqual(voice_response.status_code, 200)

        text_payload = text_response.json()
        voice_payload = voice_response.json()
        self.assertEqual(text_payload["answer"], voice_payload["answer"])
        self.assertEqual(text_payload["confidence"], voice_payload["confidence"])
        self.assertEqual(sorted(text_payload["source_memory_ids"]), sorted(voice_payload["source_memory_ids"]))

    def test_stream_failure_can_fallback_to_text_question_endpoint(self) -> None:
        self._save_expense(4.0, "eggs")

        stream_response = self.client.post(
            "/api/v1/question/stream",
            headers={**self.headers, "x-stream-disabled": "true"},
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(stream_response.status_code, 503)
        self.assertEqual(stream_response.json()["error"]["code"], "ai.provider_unavailable")

        fallback_response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(fallback_response.status_code, 200)
        payload = fallback_response.json()
        self.assertIn("answer", payload)
        self.assertIn("confidence", payload)
        self.assertIn("source_memory_ids", payload)


if __name__ == "__main__":
    unittest.main()
