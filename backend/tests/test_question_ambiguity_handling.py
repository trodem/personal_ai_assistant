import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class QuestionAmbiguityHandlingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        token = build_dev_token(f"user-ambiguity-{uuid4()}", tenant_id="tenant-a")
        self.headers = {"Authorization": f"Bearer {token}", "x-tenant-id": "tenant-a"}

    def test_text_question_returns_clarification_question_before_final_answer(self) -> None:
        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "What was my last?"},
        )
        self.assertEqual(response.status_code, 422)
        payload = response.json()
        self.assertEqual(payload["error"]["code"], "query.ambiguous_intent")
        self.assertIn("clarification_question", payload["error"]["details"])
        self.assertIn("clarification_questions", payload["error"]["details"])
        self.assertEqual(len(payload["error"]["details"]["clarification_questions"]), 1)
        self.assertEqual(
            payload["error"]["details"]["clarification_question"],
            payload["error"]["details"]["clarification_questions"][0],
        )

    def test_voice_question_returns_same_ambiguity_clarification_contract(self) -> None:
        response = self.client.post(
            "/api/v1/voice/question",
            headers=self.headers,
            files={"audio": ("question.wav", b"What was my last?", "audio/wav")},
        )
        self.assertEqual(response.status_code, 422)
        payload = response.json()
        self.assertEqual(payload["error"]["code"], "query.ambiguous_intent")
        self.assertIn("clarification_question", payload["error"]["details"])
        self.assertIn("clarification_questions", payload["error"]["details"])
        self.assertEqual(len(payload["error"]["details"]["clarification_questions"]), 1)


if __name__ == "__main__":
    unittest.main()
