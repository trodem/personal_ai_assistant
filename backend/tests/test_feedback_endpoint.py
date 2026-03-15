import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class FeedbackEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        token = build_dev_token("user-feedback", tenant_id="tenant-a")
        self.headers = {"Authorization": f"Bearer {token}", "x-tenant-id": "tenant-a"}

    def test_feedback_answer_accepts_valid_payload(self) -> None:
        response = self.client.post(
            "/api/v1/feedback/answers",
            headers=self.headers,
            json={
                "answer_id": "answer-1",
                "sentiment": "like",
                "reason": "accurate",
                "comment": "Great answer",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"accepted": True})

    def test_feedback_answer_requires_auth(self) -> None:
        response = self.client.post(
            "/api/v1/feedback/answers",
            json={"answer_id": "answer-1", "sentiment": "like"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth.missing_token")

    def test_feedback_answer_rejects_invalid_sentiment(self) -> None:
        response = self.client.post(
            "/api/v1/feedback/answers",
            headers=self.headers,
            json={"answer_id": "answer-1", "sentiment": "neutral"},
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "memory.missing_required_fields")


if __name__ == "__main__":
    unittest.main()
