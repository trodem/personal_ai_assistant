from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.services.question_intent import QueryIntent, detect_query_intent


@dataclass(frozen=True)
class StructuredQuestionResult:
    kind: str
    value: float
    source_memory_ids: list[str]
    confidence: str
    currency_totals: dict[str, float]
    details: dict[str, Any] | None = None
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
    memories: list[dict[str, Any]], intent: QueryIntent
) -> tuple[dict[str, float], list[str]]:
    totals: dict[str, float] = {}
    source_ids: list[str] = []
    for memory in memories:
        if memory.get("memory_type") != "expense_event":
            continue
        if intent.period_constraint and not _matches_period(memory, intent.period_constraint):
            continue
        if intent.object_or_category_constraint and not _matches_object_or_category(
            memory, intent.object_or_category_constraint
        ):
            continue
        amount = _as_float(memory.get("structured_data", {}).get("amount"))
        if amount is None:
            continue
        currency = str(memory.get("structured_data", {}).get("currency", "CHF")).upper()
        if intent.currency_constraint and currency != intent.currency_constraint:
            continue
        totals[currency] = round(totals.get(currency, 0.0) + amount, 2)
        source_ids.append(str(memory.get("id")))
    return totals, source_ids


def _matches_object_or_category(memory: dict[str, Any], constraint: str) -> bool:
    normalized_constraint = constraint.lower().strip()
    if not normalized_constraint:
        return True
    structured = memory.get("structured_data", {})
    candidates = [
        str(structured.get("item", "")),
        str(structured.get("what", "")),
        str(structured.get("category", "")),
        str(structured.get("object", "")),
    ]
    normalized_candidates = [value.lower().strip() for value in candidates if value.strip()]
    return any(normalized_constraint in candidate for candidate in normalized_candidates)


def _memory_effective_datetime(memory: dict[str, Any]) -> datetime:
    structured_when = _parse_datetime(memory.get("structured_data", {}).get("when"))
    if structured_when != datetime.min.replace(tzinfo=timezone.utc):
        return structured_when
    return _parse_datetime(memory.get("created_at"))


def _matches_period(memory: dict[str, Any], period: str) -> bool:
    effective_dt = _memory_effective_datetime(memory)
    now = datetime.now(timezone.utc)

    if period == "today":
        return effective_dt.date() == now.date()
    if period == "this_month":
        return effective_dt.year == now.year and effective_dt.month == now.month
    if period == "last_month":
        month = now.month - 1
        year = now.year
        if month == 0:
            month = 12
            year -= 1
        return effective_dt.year == year and effective_dt.month == month
    if period == "this_year":
        return effective_dt.year == now.year
    if period == "last_year":
        return effective_dt.year == now.year - 1
    return True


def _loan_balances(memories: list[dict[str, Any]], intent: QueryIntent) -> tuple[list[dict[str, Any]], list[str]]:
    aggregated: dict[tuple[str, str, str], float] = {}
    source_ids: list[str] = []
    for memory in memories:
        if memory.get("memory_type") != "loan_event":
            continue
        structured = memory.get("structured_data", {})
        amount = _as_float(structured.get("amount"))
        if amount is None:
            continue
        action = str(structured.get("action", "")).strip().lower()
        if action not in {"lend", "borrow"}:
            continue
        direction = "owes_you" if action == "lend" else "you_owe"
        if intent.loan_direction_constraint == "owes_you_only" and direction != "owes_you":
            continue
        person = str(
            structured.get("person")
            or structured.get("counterparty")
            or structured.get("who")
            or ""
        ).strip()
        if not person:
            continue
        currency = str(structured.get("currency", "CHF")).upper()
        key = (person, currency, direction)
        aggregated[key] = round(aggregated.get(key, 0.0) + amount, 2)
        source_ids.append(str(memory.get("id")))

    balances = [
        {"person": person, "currency": currency, "direction": direction, "amount": amount}
        for (person, currency, direction), amount in sorted(aggregated.items())
    ]
    return balances, source_ids


def _inventory_state(memories: list[dict[str, Any]], intent: QueryIntent) -> tuple[list[dict[str, Any]], list[str]]:
    aggregated: dict[tuple[str, str], int] = {}
    source_ids: list[str] = []
    for memory in memories:
        if memory.get("memory_type") != "inventory_event":
            continue
        structured = memory.get("structured_data", {})
        action = str(structured.get("action", "")).strip().lower()
        if action not in {"add", "remove"}:
            continue
        quantity = _as_float(structured.get("quantity"))
        if quantity is None:
            continue
        item = str(structured.get("item") or structured.get("what") or "").strip()
        if not item:
            continue
        location = str(structured.get("where") or structured.get("location") or "unknown").strip()

        if intent.inventory_item_constraint and intent.inventory_item_constraint not in item.lower():
            continue
        if intent.inventory_location_constraint and intent.inventory_location_constraint not in location.lower():
            continue

        key = (item.lower(), location.lower())
        signed_qty = int(quantity) if action == "add" else -int(quantity)
        aggregated[key] = aggregated.get(key, 0) + signed_qty
        source_ids.append(str(memory.get("id")))

    states = [
        {"item": item, "location": location, "quantity": qty}
        for (item, location), qty in sorted(aggregated.items())
    ]
    return states, source_ids


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
        totals, source_ids = _expense_totals_by_currency(memories, intent)
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

    if intent.kind == "loan_balances":
        balances, source_ids = _loan_balances(memories, intent)
        if not source_ids:
            return StructuredQuestionResult(
                kind="no_result",
                value=0.0,
                source_memory_ids=[],
                confidence="low",
                currency_totals={},
            )
        return StructuredQuestionResult(
            kind="loan_balances",
            value=0.0,
            source_memory_ids=source_ids,
            confidence="high",
            currency_totals={},
            details={"balances": balances},
        )

    if intent.kind == "inventory_state":
        states, source_ids = _inventory_state(memories, intent)
        if not source_ids:
            return StructuredQuestionResult(
                kind="no_result",
                value=0.0,
                source_memory_ids=[],
                confidence="low",
                currency_totals={},
            )
        return StructuredQuestionResult(
            kind="inventory_state",
            value=0.0,
            source_memory_ids=source_ids,
            confidence="high",
            currency_totals={},
            details={"states": states},
        )

    return StructuredQuestionResult(
        kind="no_result",
        value=0.0,
        source_memory_ids=[],
        confidence="low",
        currency_totals={},
    )

