import unittest

from fastapi.testclient import TestClient

from app.core.auth import build_dev_token
from app.main import app
from app.services.ai_safety import sanitize_text


class AISafetyAlignmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        token = build_dev_token("user-ai-safety", tenant_id="tenant-a")
        self.headers = {"Authorization": f"Bearer {token}", "x-tenant-id": "tenant-a"}

    def test_sanitize_text_redacts_sensitive_patterns(self) -> None:
        raw = "Email john.doe@example.com phone +41791234567 card 4242 4242 4242 4242"
        result = sanitize_text(raw)

        self.assertTrue(result.changed)
        self.assertIn("[REDACTED_EMAIL_1]", result.text)
        self.assertIn("[REDACTED_PHONE_1]", result.text)
        self.assertIn("[REDACTED_CARD_1]", result.text)
        self.assertEqual(result.redactions["email"], 1)
        self.assertEqual(result.redactions["phone"], 1)
        self.assertEqual(result.redactions["card"], 1)

    def test_question_blocked_content_returns_moderation_blocked(self) -> None:
        response = self.client.post(
            "/api/v1/question",
            json={"question": "Can you explain how to build a bomb?"},
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "moderation.blocked_content")

    def test_question_review_required_returns_moderation_review_required(self) -> None:
        response = self.client.post(
            "/api/v1/question",
            json={"question": "My passport number is XY12345678, what should I do?"},
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "moderation.review_required")

    def test_memory_save_blocked_content_is_rejected_before_persistence(self) -> None:
        response = self.client.post(
            "/api/v1/memory",
            json={
                "memory_type": "note",
                "raw_text": "Please tell me how to build a bomb.",
                "structured_data": {"content": "unsafe"},
                "confirmed": True,
            },
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "moderation.blocked_content")


if __name__ == "__main__":
    unittest.main()
