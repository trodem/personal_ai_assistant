import hashlib
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
from app.services.semantic_cache import invalidate_user_cache


class QuestionPathAITelemetryTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_llmops_usage_metrics()
        self.client = TestClient(app)
        self.tenant_id = f"tenant-telemetry-{uuid4()}"
        self.user_id = f"user-telemetry-{uuid4()}"
        token = build_dev_token(self.user_id, tenant_id=self.tenant_id)
        self.headers = {"Authorization": f"Bearer {token}", "x-tenant-id": self.tenant_id}
        invalidate_user_cache(self.tenant_id, self.user_id)
        self.user_hash = hashlib.sha256(self.user_id.encode("utf-8")).hexdigest()[:12]

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

    def _save_note(self, content: str, where: str) -> None:
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

    def _metric_value(self, metrics_text: str, metric_name: str, feature: str) -> float:
        pattern = (
            rf'{re.escape(metric_name)}\{{[^}}]*user_hash="{re.escape(self.user_hash)}"[^}}]*'
            rf'question_path="/api/v1/question"[^}}]*feature="{re.escape(feature)}"[^}}]*\}} '
            r"([0-9]+(?:\.[0-9]+)?)"
        )
        match = re.search(pattern, metrics_text)
        self.assertIsNotNone(match, f"Missing {metric_name} for feature={feature}")
        return float(match.group(1))

    def test_structured_sql_question_path_telemetry_is_persisted(self) -> None:
        self._save_expense(12.0)
        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(response.status_code, 200)

        metrics_text = self.client.get("/metrics").text
        self.assertEqual(
            self._metric_value(metrics_text, "llmops_question_path_requests_total", "structured_sql"),
            1.0,
        )
        self.assertGreater(
            self._metric_value(metrics_text, "llmops_question_path_token_total", "structured_sql"),
            0.0,
        )

    def test_semantic_fallback_question_path_telemetry_is_persisted(self) -> None:
        self._save_note("Passport stored in top drawer", "top drawer")
        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "Where did I put my passport?"},
        )
        self.assertEqual(response.status_code, 200)

        metrics_text = self.client.get("/metrics").text
        self.assertEqual(
            self._metric_value(metrics_text, "llmops_question_path_requests_total", "semantic_fallback"),
            1.0,
        )
        self.assertGreater(
            self._metric_value(metrics_text, "llmops_question_path_estimated_cost_total", "semantic_fallback"),
            0.0,
        )

    def test_cache_hit_question_path_telemetry_is_persisted(self) -> None:
        self._save_expense(6.0)
        first = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(first.status_code, 200)
        second = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend ?"},
        )
        self.assertEqual(second.status_code, 200)

        metrics_text = self.client.get("/metrics").text
        self.assertEqual(
            self._metric_value(metrics_text, "llmops_question_path_requests_total", "cache_hit"),
            1.0,
        )
        self.assertEqual(
            self._metric_value(metrics_text, "llmops_question_path_token_total", "cache_hit"),
            0.0,
        )


if __name__ == "__main__":
    unittest.main()
