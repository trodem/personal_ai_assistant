import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.memory_ingestion import apply_extraction_schema_guardrails, extract_memory_proposal


class ExtractionGuardrailsTests(unittest.TestCase):
    def test_guardrails_drop_unknown_fields_and_normalize_types(self) -> None:
        guarded = apply_extraction_schema_guardrails(
            "expense_event",
            {
                "item": " bread ",
                "amount": "3,5",
                "currency": "chf",
                "where": " coop ",
                "hacker_field": "DROP TABLE",
                "action": "remove",
                "who": 42,
            },
        )
        self.assertEqual(guarded["item"], "bread")
        self.assertEqual(guarded["amount"], 3.5)
        self.assertEqual(guarded["currency"], "CHF")
        self.assertEqual(guarded["where"], "coop")
        self.assertNotIn("hacker_field", guarded)
        self.assertNotIn("action", guarded)
        self.assertNotIn("who", guarded)

    def test_guardrails_reject_invalid_action_and_currency(self) -> None:
        guarded = apply_extraction_schema_guardrails(
            "loan_event",
            {
                "counterparty": "Marco",
                "amount": 50,
                "currency": "BTC",
                "action": "steal",
            },
        )
        self.assertEqual(guarded["counterparty"], "Marco")
        self.assertEqual(guarded["amount"], 50.0)
        self.assertNotIn("currency", guarded)
        self.assertNotIn("action", guarded)

    def test_extract_memory_proposal_applies_guardrails_on_extracted_payload(self) -> None:
        mocked_payload = {
            "item": "bread",
            "amount": "3",
            "currency": "CHF",
            "unknown": "unexpected",
        }
        with patch("app.services.memory_ingestion._extract_structured_data", return_value=mocked_payload):
            proposal = extract_memory_proposal("I bought bread")
        self.assertEqual(proposal.memory_type, "expense_event")
        self.assertNotIn("unknown", proposal.structured_data)
        self.assertEqual(proposal.structured_data["amount"], 3.0)


if __name__ == "__main__":
    unittest.main()
