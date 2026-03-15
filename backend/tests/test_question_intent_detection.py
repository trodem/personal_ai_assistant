import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.question_intent import detect_query_intent


class QuestionIntentDetectionTests(unittest.TestCase):
    def test_detects_expense_aggregation_intent(self) -> None:
        intent = detect_query_intent("How much did I spend this month in CHF?")
        self.assertEqual(intent.kind, "expense_aggregation")
        self.assertEqual(intent.aggregation, "sum")
        self.assertEqual(intent.target, "expense_event")
        self.assertEqual(intent.currency_constraint, "CHF")

    def test_detects_latest_lookup_intent_with_ordering_and_limit(self) -> None:
        intent = detect_query_intent("How much was my last service?")
        self.assertEqual(intent.kind, "latest_expense_lookup")
        self.assertTrue(intent.order_by_when_desc)
        self.assertEqual(intent.limit, 1)
        self.assertEqual(intent.target, "expense_event")

    def test_detects_ambiguous_last_intent(self) -> None:
        intent = detect_query_intent("What was my last?")
        self.assertEqual(intent.kind, "ambiguous_intent")
        self.assertIsNotNone(intent.clarification_question)

    def test_detects_out_of_scope_intent(self) -> None:
        intent = detect_query_intent("What is the weather tomorrow?")
        self.assertEqual(intent.kind, "out_of_scope")

    def test_detects_no_result_intent_for_unsupported_question(self) -> None:
        intent = detect_query_intent("Tell me something random")
        self.assertEqual(intent.kind, "no_result")


if __name__ == "__main__":
    unittest.main()
