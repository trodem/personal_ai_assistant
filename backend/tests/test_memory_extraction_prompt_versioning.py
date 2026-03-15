import re
import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.prompts.memory_extraction_prompt import (
    MEMORY_EXTRACTION_PROMPT_VERSION,
    build_memory_extraction_prompt,
)


class MemoryExtractionPromptVersioningTests(unittest.TestCase):
    def test_prompt_version_follows_stable_convention(self) -> None:
        self.assertRegex(MEMORY_EXTRACTION_PROMPT_VERSION, r"^memory_extraction_v\d+$")

    def test_prompt_contains_canonical_memory_types(self) -> None:
        prompt = build_memory_extraction_prompt()
        for memory_type in ("expense_event", "inventory_event", "loan_event", "note", "document"):
            self.assertIn(memory_type, prompt)
        self.assertIn("structured_data", prompt)


if __name__ == "__main__":
    unittest.main()
