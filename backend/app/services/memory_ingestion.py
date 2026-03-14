from dataclasses import dataclass
import re
from typing import Any


MEMORY_TYPES = ("expense_event", "inventory_event", "loan_event", "note", "document")

REQUIRED_FIELDS_BY_TYPE: dict[str, tuple[str, ...]] = {
    "expense_event": ("item", "amount"),
    "inventory_event": ("item", "quantity", "action"),
    "loan_event": ("counterparty", "amount"),
    "note": (),
    "document": (),
}


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

    if memory_type == "expense_event":
        if item:
            structured_data["item"] = item
        if amount is not None:
            structured_data["amount"] = amount
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
        if "to " in text.lower():
            structured_data["counterparty"] = text.lower().split("to ", 1)[1].strip()
    elif memory_type in {"note", "document"}:
        structured_data["content"] = text.strip()

    return structured_data


def missing_required_fields(memory_type: str, structured_data: dict[str, Any]) -> list[str]:
    required = REQUIRED_FIELDS_BY_TYPE.get(memory_type, ())
    return [field for field in required if field not in structured_data]


def clarification_questions_for_fields(fields: list[str]) -> list[str]:
    questions = {
        "item": "What is the item?",
        "amount": "What is the amount?",
        "quantity": "What is the quantity?",
        "action": "Is this an add or remove action?",
        "counterparty": "Who is the counterparty?",
    }
    # AI UX contract: ask one concise clarification question per turn.
    for field in fields:
        if field in questions:
            return [questions[field]]
    return []


def extract_memory_proposal(transcript: str) -> ExtractionResult:
    memory_type = classify_memory_type(transcript)
    structured_data = _extract_structured_data(memory_type, transcript)
    missing_fields = missing_required_fields(memory_type, structured_data)
    clarification_questions = clarification_questions_for_fields(missing_fields)
    return ExtractionResult(
        transcript=transcript,
        memory_type=memory_type,
        structured_data=structured_data,
        clarification_questions=clarification_questions,
        missing_required_fields=missing_fields,
        needs_confirmation=len(missing_fields) == 0,
    )
