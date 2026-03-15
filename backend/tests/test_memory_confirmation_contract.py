import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class MemoryConfirmationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        token = build_dev_token("user-confirm-contract", tenant_id="tenant-a")
        self.headers = {"Authorization": f"Bearer {token}", "x-tenant-id": "tenant-a"}

    def test_voice_memory_proposal_exposes_confirm_modify_cancel_actions(self) -> None:
        response = self.client.post(
            "/api/v1/voice/memory",
            headers=self.headers,
            files={"audio": ("memory.wav", b"I bought bread", "audio/wav")},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["confirmation_actions"], ["Confirm", "Modify", "Cancel"])
        self.assertEqual(payload["ai_state"], "needs_clarification")

    def test_persistence_is_blocked_without_explicit_confirm(self) -> None:
        response = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "expense_event",
                "raw_text": "I bought bread for 3 CHF",
                "structured_data": {"item": "bread", "amount": 3.0, "currency": "CHF"},
                "confirmed": False,
            },
        )
        self.assertEqual(response.status_code, 422)
        payload = response.json()
        self.assertEqual(payload["error"]["code"], "memory.confirmation_required")

    def test_persistence_succeeds_after_confirm(self) -> None:
        response = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "expense_event",
                "raw_text": "I bought bread for 3 CHF",
                "structured_data": {"item": "bread", "amount": 3.0, "currency": "CHF"},
                "confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["ai_state"], "saved")
        self.assertEqual(payload["memory_type"], "expense_event")


if __name__ == "__main__":
    unittest.main()
