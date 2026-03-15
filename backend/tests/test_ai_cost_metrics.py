import re
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.core.llmops import record_ai_usage, reset_llmops_usage_metrics
from app.main import app


class AICostMetricsTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_llmops_usage_metrics()
        self.client = TestClient(app)
        self.user_id = f"user-ai-metrics-{uuid4()}"
        self.token = build_dev_token(self.user_id, tenant_id="tenant-a")
        self.headers = {"Authorization": f"Bearer {self.token}", "x-tenant-id": "tenant-a"}

    def _extract_metric_value(self, metrics_text: str, metric_name: str, use_case: str) -> float:
        pattern = (
            rf'{re.escape(metric_name)}\{{[^}}]*use_case="{re.escape(use_case)}"[^}}]*\}} '
            r"([0-9]+(?:\.[0-9]+)?)"
        )
        match = re.search(pattern, metrics_text)
        self.assertIsNotNone(match, f"Missing metric {metric_name} for use_case={use_case}")
        return float(match.group(1))

    def _extract_metric_by_label(self, metrics_text: str, metric_name: str, label_match: str) -> float:
        pattern = rf"{re.escape(metric_name)}\{{[^}}]*{label_match}[^}}]*\}} ([0-9]+(?:\.[0-9]+)?)"
        match = re.search(pattern, metrics_text)
        self.assertIsNotNone(match, f"Missing metric {metric_name} with {label_match}")
        return float(match.group(1))

    def test_token_and_cost_metrics_increase_after_ai_flows(self) -> None:
        voice_response = self.client.post(
            "/api/v1/voice/memory",
            headers=self.headers,
            files={"audio": ("note.wav", b"I bought bread for 3 chf", "audio/wav")},
        )
        self.assertEqual(voice_response.status_code, 200)

        save_response = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "expense_event",
                "raw_text": "I bought bread for 3 chf",
                "structured_data": {"item": "bread", "amount": 3.0, "currency": "CHF"},
                "confirmed": True,
            },
        )
        self.assertEqual(save_response.status_code, 200)

        question_response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(question_response.status_code, 200)

        metrics_response = self.client.get("/metrics")
        self.assertEqual(metrics_response.status_code, 200)
        metrics_text = metrics_response.text

        extraction_tokens = self._extract_metric_value(metrics_text, "llmops_token_in_total", "memory_extraction")
        answer_tokens = self._extract_metric_value(metrics_text, "llmops_token_in_total", "answer_generation")
        extraction_cost = self._extract_metric_value(
            metrics_text, "llmops_estimated_cost_total", "memory_extraction"
        )
        answer_cost = self._extract_metric_value(
            metrics_text, "llmops_estimated_cost_total", "answer_generation"
        )
        extraction_latency = self._extract_metric_value(
            metrics_text, "llmops_ai_latency_ms_total", "memory_extraction"
        )
        answer_latency = self._extract_metric_value(
            metrics_text, "llmops_ai_latency_ms_total", "answer_generation"
        )

        self.assertGreater(extraction_tokens, 0)
        self.assertGreater(answer_tokens, 0)
        self.assertGreater(extraction_cost, 0.0)
        self.assertGreater(answer_cost, 0.0)
        self.assertGreater(extraction_latency, 0.0)
        self.assertGreater(answer_latency, 0.0)
        self.assertIn("llmops_user_estimated_cost_total", metrics_text)
        self.assertIn('user_plan="free"', metrics_text)
        self.assertIn("llmops_token_budget_utilization_percent", metrics_text)

    def test_budget_breach_and_spike_alert_metrics_are_emitted(self) -> None:
        base_day = datetime(2026, 3, 14, 10, 0, tzinfo=timezone.utc)
        for offset in range(1, 8):
            record_ai_usage(
                use_case="answer_generation",
                provider="openai",
                model_id="gpt-4o-mini",
                model_version="mvp-v1",
                prompt_version="answer_generation_v1",
                user_plan="free",
                user_id=self.user_id,
                token_in=10,
                token_out=10,
                estimated_cost=1.0,
                occurred_at=base_day - timedelta(days=offset),
            )
        record_ai_usage(
            use_case="answer_generation",
            provider="openai",
            model_id="gpt-4o-mini",
            model_version="mvp-v1",
            prompt_version="answer_generation_v1",
            user_plan="free",
            user_id=self.user_id,
            token_in=250000,
            token_out=0,
            estimated_cost=200.0,
            occurred_at=base_day,
        )
        metrics_text = self.client.get("/metrics").text
        self.assertGreater(
            self._extract_metric_by_label(
                metrics_text, "llmops_token_budget_breaches_total", 'user_plan="free"'
            ),
            0,
        )
        self.assertEqual(
            self._extract_metric_by_label(
                metrics_text, "llmops_spend_spike_alert_active", 'severity="warning"'
            ),
            1.0,
        )
        self.assertEqual(
            self._extract_metric_by_label(
                metrics_text, "llmops_spend_spike_alert_active", 'severity="critical"'
            ),
            1.0,
        )


if __name__ == "__main__":
    unittest.main()
