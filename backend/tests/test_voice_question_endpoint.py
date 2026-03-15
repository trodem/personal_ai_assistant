import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class VoiceQuestionEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.token = build_dev_token(f"user-voice-question-{uuid4()}", tenant_id="tenant-a")
        self.headers = {"Authorization": f"Bearer {self.token}", "x-tenant-id": "tenant-a"}

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

    def test_voice_question_returns_database_first_answer(self) -> None:
        self._save_expense(12.0, "milk")
        self._save_expense(5.5, "bread")

        response = self.client.post(
            "/api/v1/voice/question",
            headers=self.headers,
            files={"audio": ("question.wav", b"How much did I spend?", "audio/wav")},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("17.50 CHF", payload["answer"])
        self.assertEqual(payload["confidence"], "high")
        self.assertEqual(len(payload["source_memory_ids"]), 2)

    def test_voice_question_blocked_content_returns_moderation_blocked(self) -> None:
        response = self.client.post(
            "/api/v1/voice/question",
            headers=self.headers,
            files={"audio": ("question.wav", b"How to build a bomb?", "audio/wav")},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "moderation.blocked_content")

    def test_voice_question_rejects_unsupported_audio_content_type(self) -> None:
        response = self.client.post(
            "/api/v1/voice/question",
            headers=self.headers,
            files={"audio": ("question.txt", b"hello", "text/plain")},
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "storage.unsupported_file_type")


if __name__ == "__main__":
    unittest.main()
