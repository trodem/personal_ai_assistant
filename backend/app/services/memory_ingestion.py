from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any

from app.services.time_normalization import normalize_relative_when_from_text


MEMORY_TYPES = ("expense_event", "inventory_event", "loan_event", "note", "document")
SEMANTIC_FIELDS = ("who", "what", "where", "when", "why", "how")
ALLOWED_CURRENCIES = {"CHF", "EUR", "USD"}


@dataclass(frozen=True)
class ExtractionResult:
    transcript: str
    memory_type: str
    structured_data: dict[str, Any]
    clarification_questions: list[str]
    missing_required_fields: list[str]
    needs_confirmation: bool


def classify_memory_type(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ("bought", "spent", "paid", "cost")):
        return "expense_event"
    if any(token in lowered for token in ("stored", "added", "removed", "took")):
        return "inventory_event"
    if any(token in lowered for token in ("lent", "borrowed", "loan")):
        return "loan_event"
    if any(token in lowered for token in ("invoice", "receipt", "document")):
        return "document"
    return "note"


def _extract_amount(text: str) -> float | None:
    match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:chf|eur|usd)?", text.lower())
    if not match:
        return None
    return float(match.group(1).replace(",", "."))


def _extract_currency(text: str) -> str | None:
    lowered = text.lower()
    if "chf" in lowered or "franc" in lowered:
        return "CHF"
    if "eur" in lowered or "euro" in lowered:
        return "EUR"
    if "usd" in lowered or "dollar" in lowered:
        return "USD"
    return None


def _extract_where(text: str) -> str | None:
    lowered = text.lower()
    match = re.search(r"\b(?:at|in|from)\s+([a-z0-9][a-z0-9\s_-]{1,40})", lowered)
    if not match:
        return None
    value = match.group(1).strip()
    for stop_token in (" for ", " because ", " using ", " with ", " on "):
        if stop_token in value:
            value = value.split(stop_token, 1)[0].strip()
    return value or None


def _extract_when(text: str) -> str | None:
    iso_date = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    if iso_date:
        return iso_date.group(1)
    local_date = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", text)
    if local_date:
        day, month, year = local_date.group(1).split("/")
        return f"{year}-{month}-{day}"
    normalized_relative = normalize_relative_when_from_text(text)
    if normalized_relative:
        return normalized_relative
    return None


def _extract_why(text: str) -> str | None:
    lowered = text.lower()
    for marker in ("because ", "for "):
        if marker in lowered:
            tail = lowered.split(marker, 1)[1].strip()
            if tail:
                return tail[:80].strip()
    return None


def _extract_how(text: str) -> str | None:
    lowered = text.lower()
    for marker in ("using ", "via ", "by "):
        if marker in lowered:
            tail = lowered.split(marker, 1)[1].strip()
            if tail:
                return tail[:80].strip()
    return None


def _extract_semantic_fields(memory_type: str, text: str, structured_data: dict[str, Any]) -> dict[str, Any]:
    semantic: dict[str, Any] = {}
    lowered = text.lower()

    if " i " in f" {lowered} " or lowered.startswith("i "):
        semantic["who"] = "user"
    if memory_type == "loan_event" and _is_non_empty(structured_data.get("counterparty")):
        semantic["who"] = structured_data["counterparty"]

    if _is_non_empty(structured_data.get("item")):
        semantic["what"] = structured_data["item"]
    elif _is_non_empty(structured_data.get("content")):
        semantic["what"] = structured_data["content"]

    extracted_where = _extract_where(text)
    if extracted_where:
        semantic["where"] = extracted_where

    extracted_when = _extract_when(text)
    if extracted_when:
        semantic["when"] = extracted_when

    extracted_why = _extract_why(text)
    if extracted_why:
        semantic["why"] = extracted_why

    extracted_how = _extract_how(text)
    if extracted_how:
        semantic["how"] = extracted_how

    return semantic


def _extract_item(text: str) -> str | None:
    lowered = text.lower()
    for marker in ("bought", "spent on", "stored", "added", "removed", "lent to", "borrowed from"):
        if marker in lowered:
            tail = lowered.split(marker, 1)[1].strip()
            if not tail:
                return None
            return tail.split(" for ")[0].split(" at ")[0].strip()
    return None


def _extract_structured_data(memory_type: str, text: str) -> dict[str, Any]:
    structured_data: dict[str, Any] = {}
    item = _extract_item(text)
    amount = _extract_amount(text)
    currency = _extract_currency(text)

    if memory_type == "expense_event":
        if item:
            structured_data["item"] = item
        if amount is not None:
            structured_data["amount"] = amount
        if currency:
            structured_data["currency"] = currency
    elif memory_type == "inventory_event":
        if item:
            structured_data["item"] = item
        quantity = _extract_amount(text)
        if quantity is not None:
            structured_data["quantity"] = int(quantity)
        if "remove" in text.lower() or "took" in text.lower():
            structured_data["action"] = "remove"
        elif "add" in text.lower() or "stored" in text.lower():
            structured_data["action"] = "add"
    elif memory_type == "loan_event":
        if amount is not None:
            structured_data["amount"] = amount
        if currency:
            structured_data["currency"] = currency
        if "to " in text.lower():
            structured_data["counterparty"] = text.lower().split("to ", 1)[1].strip()
            structured_data["action"] = "lend"
        elif "from " in text.lower():
            structured_data["counterparty"] = text.lower().split("from ", 1)[1].strip()
            structured_data["action"] = "borrow"
    elif memory_type in {"note", "document"}:
        structured_data["content"] = text.strip()

    structured_data.update(_extract_semantic_fields(memory_type, text, structured_data))
    return structured_data


def _apply_default_when_if_missing(structured_data: dict[str, Any]) -> None:
    if not _is_non_empty(structured_data.get("when")):
        structured_data["when"] = datetime.now(timezone.utc).isoformat()


def apply_extraction_schema_guardrails(memory_type: str, structured_data: dict[str, Any]) -> dict[str, Any]:
    if memory_type not in MEMORY_TYPES:
        return {}

    allowed_fields: set[str] = set(SEMANTIC_FIELDS)
    if memory_type == "expense_event":
        allowed_fields.update({"item", "amount", "currency"})
    elif memory_type == "inventory_event":
        allowed_fields.update({"item", "quantity", "action"})
    elif memory_type == "loan_event":
        allowed_fields.update({"person", "counterparty", "amount", "currency", "action"})
    elif memory_type == "note":
        allowed_fields.update({"content"})
    elif memory_type == "document":
        allowed_fields.update({"content", "attachment_url", "attachment_id"})

    normalized: dict[str, Any] = {}
    for key, raw_value in structured_data.items():
        if key not in allowed_fields:
            continue
        if key in {"item", "content", "person", "counterparty", *SEMANTIC_FIELDS, "attachment_url", "attachment_id"}:
            normalized_value = _normalize_string(raw_value)
            if normalized_value is not None:
                normalized[key] = normalized_value
            continue
        if key == "amount":
            normalized_amount = _normalize_float(raw_value)
            if normalized_amount is not None:
                normalized[key] = normalized_amount
            continue
        if key == "quantity":
            normalized_quantity = _normalize_positive_int(raw_value)
            if normalized_quantity is not None:
                normalized[key] = normalized_quantity
            continue
        if key == "currency":
            normalized_currency = _normalize_currency(raw_value)
            if normalized_currency is not None:
                normalized[key] = normalized_currency
            continue
        if key == "action":
            normalized_action = _normalize_action(memory_type, raw_value)
            if normalized_action is not None:
                normalized[key] = normalized_action
            continue

    return normalized


def _normalize_string(value: Any, max_length: int = 500) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    return cleaned[:max_length]


def _normalize_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        number = float(value)
    elif isinstance(value, str):
        candidate = value.strip().replace(",", ".")
        if not candidate:
            return None
        try:
            number = float(candidate)
        except ValueError:
            return None
    else:
        return None
    if number <= 0:
        return None
    return number


def _normalize_positive_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        number = value
    elif isinstance(value, float):
        number = int(value)
    elif isinstance(value, str):
        candidate = value.strip()
        if not candidate:
            return None
        try:
            number = int(float(candidate))
        except ValueError:
            return None
    else:
        return None
    if number <= 0:
        return None
    return number


def _normalize_currency(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip().upper()
    if cleaned not in ALLOWED_CURRENCIES:
        return None
    return cleaned


def _normalize_action(memory_type: str, value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip().lower()
    if memory_type == "inventory_event" and cleaned in {"add", "remove"}:
        return cleaned
    if memory_type == "loan_event" and cleaned in {"lend", "borrow"}:
        return cleaned
    return None


def _is_non_empty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def missing_required_fields(memory_type: str, structured_data: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    if memory_type == "expense_event":
        if not (_is_non_empty(structured_data.get("item")) or _is_non_empty(structured_data.get("what"))):
            missing.append("item_or_what")
        if not _is_non_empty(structured_data.get("amount")):
            missing.append("amount")
        if not _is_non_empty(structured_data.get("currency")):
            missing.append("currency")
        return missing

    if memory_type == "inventory_event":
        if not _is_non_empty(structured_data.get("item")):
            missing.append("item")
        if not _is_non_empty(structured_data.get("quantity")):
            missing.append("quantity")
        if not _is_non_empty(structured_data.get("action")):
            missing.append("action")
        return missing

    if memory_type == "loan_event":
        if not (_is_non_empty(structured_data.get("person")) or _is_non_empty(structured_data.get("counterparty"))):
            missing.append("person_or_counterparty")
        if not _is_non_empty(structured_data.get("amount")):
            missing.append("amount")
        if not _is_non_empty(structured_data.get("currency")):
            missing.append("currency")
        if not _is_non_empty(structured_data.get("action")):
            missing.append("action")
        return missing

    if memory_type == "note":
        if not (_is_non_empty(structured_data.get("what")) or _is_non_empty(structured_data.get("content"))):
            missing.append("what_or_content")
        return missing

    if memory_type == "document":
        if not (_is_non_empty(structured_data.get("what")) or _is_non_empty(structured_data.get("content"))):
            missing.append("what_or_content")
        if not (
            _is_non_empty(structured_data.get("attachment_url"))
            or _is_non_empty(structured_data.get("attachment_id"))
        ):
            missing.append("attachment_link")
        return missing

    return missing


def clarification_questions_for_fields(
    fields: list[str],
    clarification_turn: int = 1,
    max_clarification_turns: int = 3,
) -> list[str]:
    questions = {
        "item": "What is the item?",
        "item_or_what": "What is the item or main subject?",
        "amount": "What is the amount?",
        "currency": "What is the currency?",
        "quantity": "What is the quantity?",
        "action": "Is this an add or remove action?",
        "counterparty": "Who is the counterparty?",
        "person_or_counterparty": "Who is the person involved?",
        "what_or_content": "What should be saved?",
        "attachment_link": "Please attach a receipt photo before saving this document.",
    }
    if clarification_turn > max_clarification_turns:
        return []
    # AI UX contract: ask one concise clarification question per turn.
    for field in fields:
        if field in questions:
            return [questions[field]]
    return []


def extract_memory_proposal(
    transcript: str,
    clarification_turn: int = 1,
    max_clarification_turns: int = 3,
) -> ExtractionResult:
    memory_type = classify_memory_type(transcript)
    structured_data = apply_extraction_schema_guardrails(
        memory_type,
        _extract_structured_data(memory_type, transcript),
    )
    _apply_default_when_if_missing(structured_data)
    missing_fields = missing_required_fields(memory_type, structured_data)
    clarification_questions = clarification_questions_for_fields(
        missing_fields,
        clarification_turn=clarification_turn,
        max_clarification_turns=max_clarification_turns,
    )
    return ExtractionResult(
        transcript=transcript,
        memory_type=memory_type,
        structured_data=structured_data,
        clarification_questions=clarification_questions,
        missing_required_fields=missing_fields,
        needs_confirmation=len(missing_fields) == 0,
    )
