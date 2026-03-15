import unittest
from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class MemoryIngestionE2ETests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.token = build_dev_token("user-ingestion-e2e", tenant_id="tenant-a")
        self.headers = {"Authorization": f"Bearer {self.token}", "x-tenant-id": "tenant-a"}

    def test_end_to_end_flow_requires_confirmation_and_persists_after_confirm(self) -> None:
        proposal_response = self.client.post(
            "/api/v1/voice/memory",
            headers=self.headers,
            files={"audio": ("memory.wav", b"I bought bread", "audio/wav")},
        )
        self.assertEqual(proposal_response.status_code, 200)
        proposal = proposal_response.json()
        self.assertEqual(proposal["memory_type"], "expense_event")
        self.assertEqual(len(proposal["clarification_questions"]), 1)
        self.assertIn("amount", proposal["missing_required_fields"])
        self.assertFalse(proposal["needs_confirmation"])
        self.assertEqual(proposal["ai_state"], "needs_clarification")
        self.assertEqual(proposal["source_context"], "voice")
        self.assertEqual(proposal["confirmation_actions"], ["Confirm", "Modify", "Cancel"])
        self.assertRegex(proposal["editable_datetime"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")

        rejected_save = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "expense_event",
                "raw_text": proposal["transcript"],
                "structured_data": {"item": "bread"},
                "confirmed": False,
            },
        )
        self.assertEqual(rejected_save.status_code, 422)
        self.assertEqual(rejected_save.json()["error"]["code"], "memory.confirmation_required")

        accepted_save = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "expense_event",
                "raw_text": "I bought bread for 3 chf at coop",
                "structured_data": {"item": "bread", "amount": 3.0, "location": "coop"},
                "confirmed": True,
            },
        )
        self.assertEqual(accepted_save.status_code, 200)
        saved = accepted_save.json()
        self.assertEqual(saved["memory_type"], "expense_event")
        self.assertEqual(saved["ai_state"], "saved")
        self.assertEqual(saved["structured_data_schema_version"], 1)

        memories_response = self.client.get("/api/v1/memories", headers=self.headers)
        self.assertEqual(memories_response.status_code, 200)
        items = memories_response.json()["items"]
        matching = [item for item in items if item["id"] == saved["id"]]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["structured_data"]["amount"], 3.0)
        self.assertEqual(matching[0]["structured_data_schema_version"], 1)

    def test_voice_proposal_enters_ready_to_confirm_when_required_fields_are_complete(self) -> None:
        proposal_response = self.client.post(
            "/api/v1/voice/memory",
            headers=self.headers,
            files={"audio": ("memory.wav", b"I bought bread for 3 chf", "audio/wav")},
        )
        self.assertEqual(proposal_response.status_code, 200)
        proposal = proposal_response.json()
        self.assertEqual(proposal["missing_required_fields"], [])
        self.assertEqual(proposal["clarification_questions"], [])
        self.assertTrue(proposal["needs_confirmation"])
        self.assertEqual(proposal["ai_state"], "ready_to_confirm")


if __name__ == "__main__":
    unittest.main()
