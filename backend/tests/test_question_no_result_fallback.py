import re
import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class QuestionNoResultFallbackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        token = build_dev_token(f"user-no-result-{uuid4()}", tenant_id="tenant-a")
        self.headers = {"Authorization": f"Bearer {token}", "x-tenant-id": "tenant-a"}

    def _assert_no_result_contract(self, payload: dict[str, object]) -> None:
        answer = str(payload["answer"])
        self.assertEqual(payload["confidence"], "low")
        self.assertEqual(payload["source_memory_ids"], [])
        self.assertIn("add memory", answer.lower())
        self.assertIsNone(re.search(r"\d+(?:\.\d+)?\s(?:CHF|EUR|USD)\b", answer))

    def test_text_question_no_result_uses_non_fabricated_fallback(self) -> None:
        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(response.status_code, 200)
        self._assert_no_result_contract(response.json())

    def test_voice_question_no_result_uses_non_fabricated_fallback(self) -> None:
        response = self.client.post(
            "/api/v1/voice/question",
            headers=self.headers,
            files={"audio": ("question.wav", b"How much did I spend?", "audio/wav")},
        )
        self.assertEqual(response.status_code, 200)
        self._assert_no_result_contract(response.json())


if __name__ == "__main__":
    unittest.main()
