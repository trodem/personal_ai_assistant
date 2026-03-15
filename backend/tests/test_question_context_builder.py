import json
import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.question_context_builder import (
    MAX_SEMANTIC_MEMORY_CHARS,
    MAX_SOURCE_IDS,
    build_minimal_answer_context,
)
from app.services.question_engine import StructuredQuestionResult


class QuestionContextBuilderTests(unittest.TestCase):
    def test_builder_limits_source_ids_and_keeps_compact_currency_totals(self) -> None:
        result = StructuredQuestionResult(
            kind="expenses_total",
            value=42.3456,
            source_memory_ids=[f"id-{index}" for index in range(10)],
            confidence="high",
            currency_totals={"USD": 10, "CHF": 32.3456},
        )
        payload = json.loads(
            build_minimal_answer_context(
                question="How much did I spend this month?",
                preferred_language="EN",
                structured_result=result,
            )
        )
        self.assertEqual(len(payload["source_memory_ids"]), MAX_SOURCE_IDS)
        self.assertEqual(payload["currency_totals"], {"CHF": 32.35, "USD": 10.0})
        self.assertEqual(payload["value"], 42.35)
        self.assertEqual(payload["language"], "en")

    def test_builder_truncates_semantic_match_memory_snippet(self) -> None:
        long_memory = "passport-note-" + ("x" * 500)
        result = StructuredQuestionResult(
            kind="semantic_match",
            value=0.0,
            source_memory_ids=["id-1"],
            confidence="medium",
            currency_totals={},
            details={
                "matched_memory": long_memory,
                "matched_where": "top drawer near the hallway",
                "semantic_score": 0.987654321,
            },
        )
        payload = json.loads(
            build_minimal_answer_context(
                question="Where did I put my passport?",
                preferred_language="it",
                structured_result=result,
            )
        )
        details = payload["details"]
        self.assertLessEqual(len(details["matched_memory"]), MAX_SEMANTIC_MEMORY_CHARS + 3)
        self.assertTrue(details["matched_memory"].endswith("..."))
        self.assertEqual(details["semantic_score"], 0.9877)
        self.assertEqual(details["matched_where"], "top drawer near the hallway")


if __name__ == "__main__":
    unittest.main()
