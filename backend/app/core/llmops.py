import os
from dataclasses import dataclass
import logging
from collections import defaultdict
from math import ceil
from typing import DefaultDict


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

logger = logging.getLogger("app.core.llmops")

_MetricKey = tuple[str, str, str, str, str, str, str]
_ERROR_CLASS_PROVIDER = "provider"

_REQUESTS_TOTAL: DefaultDict[_MetricKey, int] = defaultdict(int)
_ERRORS_TOTAL: DefaultDict[tuple[_MetricKey, str], int] = defaultdict(int)
_TOKEN_IN_TOTAL: DefaultDict[_MetricKey, int] = defaultdict(int)
_TOKEN_OUT_TOTAL: DefaultDict[_MetricKey, int] = defaultdict(int)
_ESTIMATED_COST_TOTAL: DefaultDict[_MetricKey, float] = defaultdict(float)

_COST_PER_TOKEN_IN = 0.00000015
_COST_PER_TOKEN_OUT = 0.00000060


def _metric_key(
    *,
    use_case: str,
    provider: str,
    model_id: str,
    model_version: str,
    prompt_version: str,
    user_plan: str,
) -> _MetricKey:
    env = os.getenv("APP_ENV", "dev")
    return (
        env,
        use_case,
        provider,
        model_id,
        model_version,
        prompt_version,
        user_plan,
    )


def _safe_token_estimate(text: str) -> int:
    cleaned = text.strip()
    if not cleaned:
        return 0
    # Deterministic MVP approximation until provider-native token usage is integrated.
    return max(1, ceil(len(cleaned) / 4))


def estimate_tokens_and_cost(*, input_text: str, output_text: str) -> tuple[int, int, float]:
    token_in = _safe_token_estimate(input_text)
    token_out = _safe_token_estimate(output_text)
    estimated_cost = round((token_in * _COST_PER_TOKEN_IN) + (token_out * _COST_PER_TOKEN_OUT), 8)
    return token_in, token_out, estimated_cost


def plan_for_role(role: str) -> str:
    return "premium" if role in {"admin", "author"} else "free"


def record_ai_usage(
    *,
    use_case: str,
    provider: str,
    model_id: str,
    model_version: str,
    prompt_version: str,
    user_plan: str,
    token_in: int,
    token_out: int,
    estimated_cost: float,
    error_class: str | None = None,
) -> None:
    key = _metric_key(
        use_case=use_case,
        provider=provider,
        model_id=model_id,
        model_version=model_version,
        prompt_version=prompt_version,
        user_plan=user_plan,
    )
    _REQUESTS_TOTAL[key] += 1
    _TOKEN_IN_TOTAL[key] += max(0, token_in)
    _TOKEN_OUT_TOTAL[key] += max(0, token_out)
    _ESTIMATED_COST_TOTAL[key] += max(0.0, estimated_cost)
    if error_class:
        _ERRORS_TOTAL[(key, error_class)] += 1

    logger.info(
        "ai_usage_recorded",
        extra={
            "ai_usage": {
                "environment": key[0],
                "use_case": key[1],
                "provider": key[2],
                "model_id": key[3],
                "model_version": key[4],
                "prompt_version": key[5],
                "user_plan": key[6],
                "token_in": token_in,
                "token_out": token_out,
                "estimated_cost": round(estimated_cost, 8),
                "error_class": error_class,
            }
        },
    )


def reset_llmops_usage_metrics() -> None:
    _REQUESTS_TOTAL.clear()
    _ERRORS_TOTAL.clear()
    _TOKEN_IN_TOTAL.clear()
    _TOKEN_OUT_TOTAL.clear()
    _ESTIMATED_COST_TOTAL.clear()


def _labels_from_key(key: _MetricKey) -> str:
    env, use_case, provider, model_id, model_version, prompt_version, user_plan = key
    return (
        f'environment="{env}",'
        f'use_case="{use_case}",'
        f'provider="{provider}",'
        f'model_id="{model_id}",'
        f'model_version="{model_version}",'
        f'prompt_version="{prompt_version}",'
        f'user_plan="{user_plan}"'
    )


def render_llmops_prometheus() -> str:
    env = os.getenv("APP_ENV", "dev")
    default_key = _metric_key(
        use_case="memory_extraction",
        provider="openai",
        model_id="unconfigured",
        model_version="unconfigured",
        prompt_version="unconfigured",
        user_plan="free",
    )
    series_keys = sorted(set(_REQUESTS_TOTAL.keys()) | {default_key})

    lines = [
        "# HELP llmops_ai_requests_total AI requests tracked for LLMOps dashboards.",
        "# TYPE llmops_ai_requests_total counter",
        "# HELP llmops_ai_errors_total AI errors tracked for LLMOps dashboards.",
        "# TYPE llmops_ai_errors_total counter",
        "# HELP llmops_token_in_total Input tokens tracked for LLMOps cost dashboard.",
        "# TYPE llmops_token_in_total counter",
        "# HELP llmops_token_out_total Output tokens tracked for LLMOps cost dashboard.",
        "# TYPE llmops_token_out_total counter",
        "# HELP llmops_estimated_cost_total Estimated cost tracked for LLMOps cost dashboard.",
        "# TYPE llmops_estimated_cost_total counter",
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

    for key in series_keys:
        labels = _labels_from_key(key)
        lines.append(f'llmops_ai_requests_total{{{labels}}} {_REQUESTS_TOTAL.get(key, 0)}')
        lines.append(
            f'llmops_ai_errors_total{{{labels},error_class="{_ERROR_CLASS_PROVIDER}"}} '
            f'{_ERRORS_TOTAL.get((key, _ERROR_CLASS_PROVIDER), 0)}'
        )
        lines.append(f"llmops_token_in_total{{{labels}}} {_TOKEN_IN_TOTAL.get(key, 0)}")
        lines.append(f"llmops_token_out_total{{{labels}}} {_TOKEN_OUT_TOTAL.get(key, 0)}")
        lines.append(
            f"llmops_estimated_cost_total{{{labels}}} "
            f'{format(_ESTIMATED_COST_TOTAL.get(key, 0.0), ".8f")}'
        )

    for threshold in ALERT_THRESHOLDS:
        lines.append(
            f'llmops_alert_threshold{{metric="{threshold.metric}",severity="{threshold.severity}",window="{threshold.window}",unit="{threshold.unit}",environment="{env}"}} {threshold.value}'
        )

    return "\n".join(lines) + "\n"
