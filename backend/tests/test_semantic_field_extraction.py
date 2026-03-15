import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.memory_ingestion import extract_memory_proposal


class SemanticFieldExtractionTests(unittest.TestCase):
    def test_extracts_semantic_fields_for_expense_event(self) -> None:
        proposal = extract_memory_proposal(
            "I bought bread for 3 CHF at coop on 2026-03-15 because weekly groceries using card"
        )
        self.assertEqual(proposal.memory_type, "expense_event")
        self.assertEqual(proposal.structured_data.get("who"), "user")
        self.assertEqual(proposal.structured_data.get("what"), "bread")
        self.assertEqual(proposal.structured_data.get("where"), "coop")
        self.assertEqual(proposal.structured_data.get("when"), "2026-03-15")
        self.assertIn("weekly groceries", str(proposal.structured_data.get("why", "")))
        self.assertIn("card", str(proposal.structured_data.get("how", "")))

    def test_extracts_semantic_fields_for_note_content(self) -> None:
        proposal = extract_memory_proposal("Remember to renew insurance in Zurich on 2026-04-01")
        self.assertEqual(proposal.memory_type, "note")
        self.assertEqual(proposal.structured_data.get("what"), "Remember to renew insurance in Zurich on 2026-04-01")
        self.assertEqual(proposal.structured_data.get("where"), "zurich")
        self.assertEqual(proposal.structured_data.get("when"), "2026-04-01")

    def test_extracts_loan_counterparty_as_semantic_who(self) -> None:
        proposal = extract_memory_proposal("I lent 200 CHF to Marco on 2026-03-03")
        self.assertEqual(proposal.memory_type, "loan_event")
        self.assertEqual(proposal.structured_data.get("counterparty"), "marco on 2026-03-03")
        self.assertEqual(proposal.structured_data.get("who"), "marco on 2026-03-03")
        self.assertEqual(proposal.structured_data.get("action"), "lend")
        self.assertEqual(proposal.structured_data.get("when"), "2026-03-03")

    def test_applies_default_when_timestamp_if_missing_in_text(self) -> None:
        before = datetime.now(timezone.utc) - timedelta(seconds=2)
        proposal = extract_memory_proposal("I bought milk for 2 CHF at coop")
        after = datetime.now(timezone.utc) + timedelta(seconds=2)
        when_value = proposal.structured_data.get("when")
        self.assertIsInstance(when_value, str)
        parsed = datetime.fromisoformat(str(when_value))
        self.assertGreaterEqual(parsed, before)
        self.assertLessEqual(parsed, after)

    def test_keeps_explicit_when_value_when_provided(self) -> None:
        proposal = extract_memory_proposal("I bought milk for 2 CHF on 2026-06-10")
        self.assertEqual(proposal.structured_data.get("when"), "2026-06-10")

    def test_normalizes_relative_when_today_in_proposal(self) -> None:
        before = datetime.now(timezone.utc) - timedelta(seconds=2)
        proposal = extract_memory_proposal("I bought milk for 2 CHF today")
        after = datetime.now(timezone.utc) + timedelta(seconds=2)
        when_value = proposal.structured_data.get("when")
        self.assertIsInstance(when_value, str)
        parsed = datetime.fromisoformat(str(when_value))
        self.assertGreaterEqual(parsed, before)
        self.assertLessEqual(parsed, after)


if __name__ == "__main__":
    unittest.main()
