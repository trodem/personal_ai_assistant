import os
from dataclasses import dataclass


STANDARD_DIMENSIONS = (
    "environment",
    "use_case",
    "provider",
    "model_id",
    "model_version",
    "prompt_version",
    "user_plan",
)


@dataclass(frozen=True)
class AlertThreshold:
    metric: str
    severity: str
    window: str
    value: float
    unit: str


ALERT_THRESHOLDS = (
    AlertThreshold("ai_endpoint_latency_p95", "warning", "10m", 12, "seconds"),
    AlertThreshold("ai_endpoint_latency_p95", "critical", "5m", 20, "seconds"),
    AlertThreshold("ai_5xx_rate", "warning", "5m", 3, "percent"),
    AlertThreshold("ai_5xx_rate", "critical", "5m", 8, "percent"),
    AlertThreshold("provider_failure_rate", "warning", "10m", 5, "percent"),
    AlertThreshold("daily_spend_vs_7d_ma", "warning", "1d", 120, "percent"),
    AlertThreshold("daily_spend_vs_7d_ma", "critical", "1d", 160, "percent"),
    AlertThreshold("monthly_budget_burn_projection", "warning", "30d", 110, "percent"),
    AlertThreshold("monthly_budget_burn_projection", "critical", "30d", 130, "percent"),
    AlertThreshold("extraction_confirmation_rate", "warning", "24h", 85, "percent_min"),
    AlertThreshold("question_no_result_rate", "warning", "24h", 20, "percent_max"),
    AlertThreshold("ocr_failed_rate", "warning", "1h", 15, "percent"),
)


def render_llmops_prometheus() -> str:
    env = os.getenv("APP_ENV", "dev")
    use_case = "memory_extraction"
    provider = "openai"
    model_id = "unconfigured"
    model_version = "unconfigured"
    prompt_version = "unconfigured"
    user_plan = "free"

    dim_labels = (
        f'environment="{env}",'
        f'use_case="{use_case}",'
        f'provider="{provider}",'
        f'model_id="{model_id}",'
        f'model_version="{model_version}",'
        f'prompt_version="{prompt_version}",'
        f'user_plan="{user_plan}"'
    )

    lines = [
        "# HELP llmops_ai_requests_total AI requests tracked for LLMOps dashboards.",
        "# TYPE llmops_ai_requests_total counter",
        f"llmops_ai_requests_total{{{dim_labels}}} 0",
        "# HELP llmops_ai_errors_total AI errors tracked for LLMOps dashboards.",
        "# TYPE llmops_ai_errors_total counter",
        f"llmops_ai_errors_total{{{dim_labels},error_class=\"provider\"}} 0",
        "# HELP llmops_token_in_total Input tokens tracked for LLMOps cost dashboard.",
        "# TYPE llmops_token_in_total counter",
        f"llmops_token_in_total{{{dim_labels}}} 0",
        "# HELP llmops_token_out_total Output tokens tracked for LLMOps cost dashboard.",
        "# TYPE llmops_token_out_total counter",
        f"llmops_token_out_total{{{dim_labels}}} 0",
        "# HELP llmops_estimated_cost_total Estimated cost tracked for LLMOps cost dashboard.",
        "# TYPE llmops_estimated_cost_total counter",
        f"llmops_estimated_cost_total{{{dim_labels}}} 0",
        "# HELP llmops_extraction_confirmation_rate Extraction confirmation rate for LLMOps quality dashboard.",
        "# TYPE llmops_extraction_confirmation_rate gauge",
        f'llmops_extraction_confirmation_rate{{environment="{env}"}} 0',
        "# HELP llmops_question_no_result_rate Question no-result rate for LLMOps quality dashboard.",
        "# TYPE llmops_question_no_result_rate gauge",
        f'llmops_question_no_result_rate{{environment="{env}"}} 0',
        "# HELP llmops_ocr_failed_rate OCR failed rate for LLMOps quality dashboard.",
        "# TYPE llmops_ocr_failed_rate gauge",
        f'llmops_ocr_failed_rate{{environment="{env}"}} 0',
        "# HELP llmops_semantic_cache_hit_ratio Semantic cache hit ratio for LLMOps quality dashboard.",
        "# TYPE llmops_semantic_cache_hit_ratio gauge",
        f'llmops_semantic_cache_hit_ratio{{environment="{env}"}} 0',
        "# HELP llmops_dependency_failure_rate Dependency failure rate for LLMOps reliability dashboard.",
        "# TYPE llmops_dependency_failure_rate gauge",
        f'llmops_dependency_failure_rate{{environment="{env}",provider="openai"}} 0',
        "# HELP llmops_alert_threshold LLMOps alert thresholds from docs/llmops-dashboard-spec.md.",
        "# TYPE llmops_alert_threshold gauge",
    ]

    for threshold in ALERT_THRESHOLDS:
        lines.append(
            f'llmops_alert_threshold{{metric="{threshold.metric}",severity="{threshold.severity}",window="{threshold.window}",unit="{threshold.unit}",environment="{env}"}} {threshold.value}'
        )

    return "\n".join(lines) + "\n"
