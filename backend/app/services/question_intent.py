from dataclasses import dataclass
import re


OUT_OF_SCOPE_KEYWORDS = ("weather", "news", "market", "stock", "bitcoin")


@dataclass(frozen=True)
class QueryIntent:
    kind: str
    aggregation: str | None = None
    target: str | None = None
    order_by_when_desc: bool = False
    limit: int | None = None
    currency_constraint: str | None = None
    period_constraint: str | None = None
    object_or_category_constraint: str | None = None
    loan_direction_constraint: str | None = None
    inventory_item_constraint: str | None = None
    inventory_location_constraint: str | None = None
    clarification_question: str | None = None


def detect_query_intent(question: str) -> QueryIntent:
    lowered = question.lower().strip()

    if any(token in lowered for token in OUT_OF_SCOPE_KEYWORDS):
        return QueryIntent(kind="out_of_scope")

    if "how much" in lowered and "spend" in lowered:
        return QueryIntent(
            kind="expense_aggregation",
            aggregation="sum",
            target="expense_event",
            currency_constraint=_currency_constraint(lowered),
            period_constraint=_period_constraint(lowered),
            object_or_category_constraint=_object_or_category_constraint(lowered),
        )

    if "how many" in lowered and (
        "left" in lowered or "remaining" in lowered or "in stock" in lowered or "do i have" in lowered
    ):
        return QueryIntent(
            kind="inventory_state",
            aggregation="state",
            target="inventory_event",
            inventory_item_constraint=_inventory_item_constraint(lowered),
            inventory_location_constraint=_inventory_location_constraint(lowered),
        )

    if "what did i store" in lowered:
        return QueryIntent(
            kind="inventory_state",
            aggregation="state",
            target="inventory_event",
            inventory_item_constraint=None,
            inventory_location_constraint=_inventory_location_constraint(lowered),
        )

    if "last" in lowered or "latest" in lowered:
        if "spend" not in lowered and "service" not in lowered and "expense" not in lowered:
            return QueryIntent(
                kind="ambiguous_intent",
                clarification_question="Do you mean your last expense or another last record?",
            )
        return QueryIntent(
            kind="latest_expense_lookup",
            target="expense_event",
            order_by_when_desc=True,
            limit=1,
        )

    if "owe" in lowered or "owes" in lowered or "loan" in lowered:
        direction_constraint = "owes_you_only" if ("owes me" in lowered or "owe me" in lowered) else None
        return QueryIntent(
            kind="loan_balances",
            aggregation="balance",
            target="loan_event",
            loan_direction_constraint=direction_constraint,
        )

    return QueryIntent(kind="no_result")


def _currency_constraint(question: str) -> str | None:
    for token in ("chf", "eur", "usd"):
        if token in question:
            return token.upper()
    return None


def _period_constraint(question: str) -> str | None:
    if "last year" in question:
        return "last_year"
    if "this year" in question:
        return "this_year"
    if "last month" in question:
        return "last_month"
    if "this month" in question:
        return "this_month"
    if "today" in question:
        return "today"
    return None


def _object_or_category_constraint(question: str) -> str | None:
    category_match = re.search(r"\bcategory\s+([a-z0-9][a-z0-9\s-]{0,40})", question)
    if category_match:
        return _normalize_filter_value(category_match.group(1))

    object_match = re.search(r"\bon\s+(?:the\s+)?([a-z0-9][a-z0-9\s-]{0,40})", question)
    if object_match:
        return _normalize_filter_value(object_match.group(1))
    return None


def _normalize_filter_value(raw_value: str) -> str:
    value = raw_value.strip()
    for tail in (
        " last year",
        " this year",
        " last month",
        " this month",
        " today",
        " in chf",
        " in eur",
        " in usd",
    ):
        if tail in value:
            value = value.split(tail, 1)[0].strip()
    value = re.sub(r"\s+", " ", value)
    return value.strip(" .,!?:;")


def _inventory_item_constraint(question: str) -> str | None:
    match = re.search(
        r"\bhow many\s+([a-z0-9][a-z0-9\s-]{0,40}?)(?:\s+(?:are|is)\s+(?:left|remaining)|\s+do i have|\s+in\b|$)",
        question,
    )
    if not match:
        return None
    return _normalize_filter_value(match.group(1))


def _inventory_location_constraint(question: str) -> str | None:
    match = re.search(r"\bin\s+(?:the\s+)?([a-z0-9][a-z0-9\s-]{0,40})", question)
    if not match:
        return None
    return _normalize_filter_value(match.group(1))
