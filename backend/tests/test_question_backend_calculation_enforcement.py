import re
import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.core.llmops import reset_llmops_usage_metrics
from app.main import app


class QuestionBackendCalculationEnforcementTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_llmops_usage_metrics()
        self.client = TestClient(app)
        self.tenant_id = f"tenant-backend-calc-{uuid4()}"
        token = build_dev_token(f"user-backend-calc-{uuid4()}", tenant_id=self.tenant_id)
        self.headers = {"Authorization": f"Bearer {token}", "x-tenant-id": self.tenant_id}

    def test_question_answer_generation_is_tracked_as_backend_deterministic(self) -> None:
        save = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "expense_event",
                "raw_text": "I bought bread for 3 CHF",
                "structured_data": {"item": "bread", "amount": 3.0, "currency": "CHF"},
                "confirmed": True,
            },
        )
        self.assertEqual(save.status_code, 200)

        question = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(question.status_code, 200)

        metrics = self.client.get("/metrics")
        self.assertEqual(metrics.status_code, 200)
        text = metrics.text

        self.assertRegex(
            text,
            r'llmops_ai_requests_total\{[^}]*use_case="answer_generation"[^}]*provider="backend"[^}]*model_id="deterministic-question-engine"[^}]*\} 1',
        )
        self.assertIsNone(
            re.search(
                r'llmops_ai_requests_total\{[^}]*use_case="answer_generation"[^}]*provider="openai"[^}]*\}',
                text,
            )
        )


if __name__ == "__main__":
    unittest.main()
