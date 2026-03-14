from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class StructuredQuestionResult:
    kind: str
    value: float
    currency: str
    source_memory_ids: list[str]
    confidence: str


def _as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def compute_structured_result(question: str, memories: list[dict[str, Any]]) -> StructuredQuestionResult:
    lowered = question.lower().strip()
    if "how much" in lowered and "spend" in lowered:
        relevant = [m for m in memories if m.get("memory_type") == "expense_event"]
        total = 0.0
        source_ids: list[str] = []
        for memory in relevant:
            amount = _as_float(memory.get("structured_data", {}).get("amount"))
            if amount is None:
                continue
            total += amount
            source_ids.append(str(memory.get("id")))
        return StructuredQuestionResult(
            kind="expenses_total",
            value=round(total, 2),
            currency="CHF",
            source_memory_ids=source_ids,
            confidence="high" if source_ids else "low",
        )

    # Deterministic no-result fallback without fabricating data.
    return StructuredQuestionResult(
        kind="no_result",
        value=0.0,
        currency="",
        source_memory_ids=[],
        confidence="low",
    )


def format_answer_from_structured_result(result: StructuredQuestionResult) -> str:
    if result.kind == "expenses_total":
        return f"You spent {result.value:.2f} {result.currency}."
    return "I could not find matching memories for your question."
