from dataclasses import dataclass


OUT_OF_SCOPE_KEYWORDS = ("weather", "news", "market", "stock", "bitcoin")


@dataclass(frozen=True)
class QueryIntent:
    kind: str
    aggregation: str | None = None
    target: str | None = None
    order_by_when_desc: bool = False
    limit: int | None = None
    currency_constraint: str | None = None
    clarification_question: str | None = None


def detect_query_intent(question: str) -> QueryIntent:
    lowered = question.lower().strip()

    if any(token in lowered for token in OUT_OF_SCOPE_KEYWORDS):
        return QueryIntent(kind="out_of_scope")

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

    if "how much" in lowered and "spend" in lowered:
        return QueryIntent(
            kind="expense_aggregation",
            aggregation="sum",
            target="expense_event",
            currency_constraint=_currency_constraint(lowered),
        )

    return QueryIntent(kind="no_result")


def _currency_constraint(question: str) -> str | None:
    for token in ("chf", "eur", "usd"):
        if token in question:
            return token.upper()
    return None
