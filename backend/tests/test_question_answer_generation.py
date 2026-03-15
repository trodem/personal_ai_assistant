import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.question_answer_generation import generate_natural_language_answer
from app.services.question_engine import StructuredQuestionResult


class QuestionAnswerGenerationTests(unittest.TestCase):
    def test_expense_answer_is_generated_from_structured_totals(self) -> None:
        result = StructuredQuestionResult(
            kind="expenses_total",
            value=15.0,
            source_memory_ids=["m1", "m2"],
            confidence="high",
            currency_totals={"CHF": 10.0, "EUR": 5.0},
        )
        answer = generate_natural_language_answer(result, "en")
        self.assertEqual(answer, "You spent 10.00 CHF + 5.00 EUR.")

    def test_semantic_match_prefers_location_phrase(self) -> None:
        result = StructuredQuestionResult(
            kind="semantic_match",
            value=0.0,
            source_memory_ids=["m1"],
            confidence="medium",
            currency_totals={},
            details={
                "matched_where": "top drawer",
                "matched_memory": "passport in top drawer",
            },
        )
        answer = generate_natural_language_answer(result, "en")
        self.assertEqual(answer, "From your memories, it appears to be in top drawer.")

    def test_no_result_answer_follows_add_memory_fallback(self) -> None:
        result = StructuredQuestionResult(
            kind="no_result",
            value=0.0,
            source_memory_ids=[],
            confidence="low",
            currency_totals={},
        )
        answer = generate_natural_language_answer(result, "de")
        self.assertIn("Add Memory", answer)


if __name__ == "__main__":
    unittest.main()
