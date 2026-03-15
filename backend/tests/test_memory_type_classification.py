import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.memory_ingestion import MEMORY_TYPES, classify_memory_type


class MemoryTypeClassificationTests(unittest.TestCase):
    def test_classifies_expense_event(self) -> None:
        self.assertEqual(classify_memory_type("I bought bread for 3 CHF"), "expense_event")

    def test_classifies_inventory_event(self) -> None:
        self.assertEqual(classify_memory_type("I stored 4 boxes of peas in the cellar"), "inventory_event")

    def test_classifies_loan_event(self) -> None:
        self.assertEqual(classify_memory_type("I lent 200 CHF to Marco"), "loan_event")

    def test_classifies_document(self) -> None:
        self.assertEqual(classify_memory_type("I uploaded a receipt document"), "document")

    def test_falls_back_to_note(self) -> None:
        self.assertEqual(classify_memory_type("Remember to call mom tomorrow"), "note")

    def test_classifier_output_is_always_canonical_memory_type(self) -> None:
        samples = (
            "I paid 20 CHF for lunch",
            "I removed two bottles from storage",
            "loan to Anna",
            "invoice upload completed",
            "Just a random personal thought",
        )
        for sample in samples:
            self.assertIn(classify_memory_type(sample), MEMORY_TYPES)


if __name__ == "__main__":
    unittest.main()
