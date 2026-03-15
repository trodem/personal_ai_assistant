import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.memory_ingestion import (
    clarification_questions_for_fields,
    extract_memory_proposal,
)


class ClarificationEngineTests(unittest.TestCase):
    def test_returns_single_question_within_max_turns(self) -> None:
        questions = clarification_questions_for_fields(
            ["amount", "currency"],
            clarification_turn=1,
            max_clarification_turns=3,
        )
        self.assertEqual(questions, ["What is the amount?"])

    def test_returns_no_question_after_turn_limit_reached(self) -> None:
        questions = clarification_questions_for_fields(
            ["amount", "currency"],
            clarification_turn=4,
            max_clarification_turns=3,
        )
        self.assertEqual(questions, [])

    def test_extract_memory_proposal_respects_turn_limit(self) -> None:
        proposal = extract_memory_proposal(
            "I bought bread",
            clarification_turn=5,
            max_clarification_turns=3,
        )
        self.assertFalse(proposal.needs_confirmation)
        self.assertEqual(proposal.clarification_questions, [])
        self.assertIn("amount", proposal.missing_required_fields)


if __name__ == "__main__":
    unittest.main()
