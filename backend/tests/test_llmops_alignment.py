import unittest
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.llmops import ALERT_THRESHOLDS, STANDARD_DIMENSIONS, render_llmops_prometheus


class LLMOpsAlignmentTests(unittest.TestCase):
    def test_standard_dimensions_are_present(self) -> None:
        self.assertEqual(
            STANDARD_DIMENSIONS,
            (
                "environment",
                "use_case",
                "provider",
                "model_id",
                "model_version",
                "prompt_version",
                "user_plan",
            ),
        )

    def test_required_mvp_thresholds_are_registered(self) -> None:
        pairs = {(t.metric, t.severity, t.window, t.value) for t in ALERT_THRESHOLDS}
        self.assertIn(("ai_endpoint_latency_p95", "warning", "10m", 12), pairs)
        self.assertIn(("ai_endpoint_latency_p95", "critical", "5m", 20), pairs)
        self.assertIn(("ai_5xx_rate", "warning", "5m", 3), pairs)
        self.assertIn(("ai_5xx_rate", "critical", "5m", 8), pairs)
        self.assertIn(("provider_failure_rate", "warning", "10m", 5), pairs)
        self.assertIn(("daily_spend_vs_7d_ma", "warning", "1d", 120), pairs)
        self.assertIn(("daily_spend_vs_7d_ma", "critical", "1d", 160), pairs)
        self.assertIn(("monthly_budget_burn_projection", "warning", "30d", 110), pairs)
        self.assertIn(("monthly_budget_burn_projection", "critical", "30d", 130), pairs)
        self.assertIn(("extraction_confirmation_rate", "warning", "24h", 85), pairs)
        self.assertIn(("question_no_result_rate", "warning", "24h", 20), pairs)
        self.assertIn(("ocr_failed_rate", "warning", "1h", 15), pairs)

    def test_metrics_output_contains_llmops_series(self) -> None:
        output = render_llmops_prometheus()
        self.assertIn("llmops_ai_requests_total", output)
        self.assertIn("llmops_token_budget_limit", output)
        self.assertIn("llmops_spend_spike_alert_active", output)
        self.assertIn("llmops_alert_threshold", output)
        self.assertIn('metric="ai_endpoint_latency_p95"', output)


if __name__ == "__main__":
    unittest.main()
