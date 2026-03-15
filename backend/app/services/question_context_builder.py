import json
from typing import Any

from app.services.question_engine import StructuredQuestionResult

MAX_SOURCE_IDS = 5
MAX_SEMANTIC_MEMORY_CHARS = 160
MAX_CLARIFICATION_CHARS = 120


def _truncate_text(value: Any, max_chars: int) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    return f"{text[:max_chars].rstrip()}..."


def _build_compact_details(result: StructuredQuestionResult) -> dict[str, Any]:
    details = result.details or {}
    if result.kind == "semantic_match":
        compact: dict[str, Any] = {}
        matched_where = _truncate_text(details.get("matched_where"), max_chars=80)
        matched_memory = _truncate_text(
            details.get("matched_memory"),
            max_chars=MAX_SEMANTIC_MEMORY_CHARS,
        )
        semantic_score_raw = details.get("semantic_score")
        if matched_where:
            compact["matched_where"] = matched_where
        if matched_memory:
            compact["matched_memory"] = matched_memory
        try:
            compact["semantic_score"] = round(float(semantic_score_raw), 4)
        except (TypeError, ValueError):
            pass
        return compact
    return {}


def build_minimal_answer_context(
    *,
    question: str,
    preferred_language: str,
    structured_result: StructuredQuestionResult,
) -> str:
    payload: dict[str, Any] = {
        "question": question.strip(),
        "language": preferred_language.lower().strip(),
        "kind": structured_result.kind,
        "confidence": structured_result.confidence,
        "source_memory_ids": structured_result.source_memory_ids[:MAX_SOURCE_IDS],
    }
    if structured_result.currency_totals:
        payload["currency_totals"] = {
            currency: round(float(total), 2)
            for currency, total in sorted(structured_result.currency_totals.items())
        }
    if structured_result.kind in {"expenses_total", "latest_expense"}:
        payload["value"] = round(float(structured_result.value), 2)
    if structured_result.clarification_question:
        payload["clarification_question"] = _truncate_text(
            structured_result.clarification_question,
            max_chars=MAX_CLARIFICATION_CHARS,
        )
    compact_details = _build_compact_details(structured_result)
    if compact_details:
        payload["details"] = compact_details
    return json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
