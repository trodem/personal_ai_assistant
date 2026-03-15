from __future__ import annotations

MEMORY_EXTRACTION_PROMPT_VERSION = "memory_extraction_v1"


def build_memory_extraction_prompt() -> str:
    return (
        "You are an information extraction system for Personal AI Assistant. "
        "Classify user transcript into one memory_type among: "
        "expense_event, inventory_event, loan_event, note, document. "
        "Extract structured_data with semantic fields when available: who, what, where, when, why, how. "
        "Follow required-by-type constraints: "
        "expense_event requires item/what, amount, currency; "
        "inventory_event requires item, quantity, action; "
        "loan_event requires person/counterparty, amount, currency, action; "
        "note requires what/content; "
        "document requires what/content. "
        "Return only deterministic JSON payload for backend confirmation flow."
    )

