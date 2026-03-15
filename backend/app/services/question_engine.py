from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.services.question_intent import detect_query_intent


@dataclass(frozen=True)
class StructuredQuestionResult:
    kind: str
    value: float
    source_memory_ids: list[str]
    confidence: str
    currency_totals: dict[str, float]
    clarification_question: str | None = None


def _as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _sorted_by_latest(memories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # Enforce deterministic ORDER BY when DESC LIMIT 1 semantics.
    return sorted(memories, key=_latest_sort_key, reverse=True)


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
    if not isinstance(value, str):
        return datetime.min.replace(tzinfo=timezone.utc)
    parsed_raw = value.strip()
    if not parsed_raw:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        parsed = datetime.fromisoformat(parsed_raw.replace("Z", "+00:00"))
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=timezone.utc)


def _latest_sort_key(memory: dict[str, Any]) -> tuple[datetime, datetime]:
    structured_when = _parse_datetime(memory.get("structured_data", {}).get("when"))
    created_at = _parse_datetime(memory.get("created_at"))
    return (structured_when, created_at)


def _expense_totals_by_currency(
    memories: list[dict[str, Any]], currency_constraint: str | None
) -> tuple[dict[str, float], list[str]]:
    totals: dict[str, float] = {}
    source_ids: list[str] = []
    for memory in memories:
        if memory.get("memory_type") != "expense_event":
            continue
        amount = _as_float(memory.get("structured_data", {}).get("amount"))
        if amount is None:
            continue
        currency = str(memory.get("structured_data", {}).get("currency", "CHF")).upper()
        if currency_constraint and currency != currency_constraint:
            continue
        totals[currency] = round(totals.get(currency, 0.0) + amount, 2)
        source_ids.append(str(memory.get("id")))
    return totals, source_ids


def compute_structured_result(question: str, memories: list[dict[str, Any]]) -> StructuredQuestionResult:
    intent = detect_query_intent(question)

    if intent.kind == "out_of_scope":
        return StructuredQuestionResult(
            kind="out_of_scope",
            value=0.0,
            source_memory_ids=[],
            confidence="low",
            currency_totals={},
        )

    if intent.kind == "ambiguous_intent":
        return StructuredQuestionResult(
            kind="ambiguous_intent",
            value=0.0,
            source_memory_ids=[],
            confidence="low",
            currency_totals={},
            clarification_question=intent.clarification_question,
        )

    if intent.kind == "latest_expense_lookup":
        latest_expense = next(
            (
                memory
                for memory in _sorted_by_latest(memories)
                if memory.get("memory_type") == "expense_event"
                and _as_float(memory.get("structured_data", {}).get("amount")) is not None
            ),
            None,
        )
        if latest_expense is None:
            return StructuredQuestionResult(
                kind="no_result",
                value=0.0,
                source_memory_ids=[],
                confidence="low",
                currency_totals={},
            )
        amount = _as_float(latest_expense.get("structured_data", {}).get("amount")) or 0.0
        currency = str(latest_expense.get("structured_data", {}).get("currency", "CHF")).upper()
        return StructuredQuestionResult(
            kind="latest_expense",
            value=round(amount, 2),
            source_memory_ids=[str(latest_expense.get("id"))],
            confidence="high",
            currency_totals={currency: round(amount, 2)},
        )

    if intent.kind == "expense_aggregation":
        totals, source_ids = _expense_totals_by_currency(memories, intent.currency_constraint)
        if not source_ids:
            return StructuredQuestionResult(
                kind="no_result",
                value=0.0,
                source_memory_ids=[],
                confidence="low",
                currency_totals={},
            )
        return StructuredQuestionResult(
            kind="expenses_total",
            value=round(sum(totals.values()), 2),
            source_memory_ids=source_ids,
            confidence="high",
            currency_totals=totals,
        )

    return StructuredQuestionResult(
        kind="no_result",
        value=0.0,
        source_memory_ids=[],
        confidence="low",
        currency_totals={},
    )


def format_answer_from_structured_result(result: StructuredQuestionResult, preferred_language: str) -> str:
    lang = preferred_language.lower()
    if lang not in {"en", "it", "de"}:
        lang = "en"

    if result.kind == "expenses_total":
        pieces = [f"{total:.2f} {currency}" for currency, total in sorted(result.currency_totals.items())]
        joined = " + ".join(pieces)
        if lang == "it":
            return f"Hai speso {joined}."
        if lang == "de":
            return f"Du hast {joined} ausgegeben."
        return f"You spent {joined}."

    if result.kind == "latest_expense":
        currency, total = next(iter(result.currency_totals.items()))
        if lang == "it":
            return f"La tua ultima spesa e stata {total:.2f} {currency}."
        if lang == "de":
            return f"Deine letzte Ausgabe war {total:.2f} {currency}."
        return f"Your last expense was {total:.2f} {currency}."

    if result.kind == "out_of_scope":
        if lang == "it":
            return "Questa domanda e fuori dallo scope MVP. Posso rispondere solo usando le memorie salvate."
        if lang == "de":
            return "Diese Frage liegt ausserhalb des MVP-Umfangs. Ich antworte nur mit gespeicherten Erinnerungen."
        return "This question is outside MVP scope. I can answer only from your stored memories."

    if result.kind == "no_result":
        if lang == "it":
            return "Non ho trovato memorie rilevanti. Puoi usare Add Memory per registrare queste informazioni."
        if lang == "de":
            return "Ich habe keine passenden Erinnerungen gefunden. Du kannst Add Memory nutzen, um diese Information zu speichern."
        return "I could not find matching memories. You can use Add Memory to record this information."

    if lang == "it":
        return result.clarification_question or "Puoi chiarire meglio la domanda?"
    if lang == "de":
        return result.clarification_question or "Kannst du die Frage bitte praezisieren?"
    return result.clarification_question or "Could you clarify your question?"
