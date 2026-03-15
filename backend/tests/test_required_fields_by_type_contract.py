import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class RequiredFieldsByTypeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        token = build_dev_token("user-required-fields", tenant_id="tenant-a")
        self.headers = {"Authorization": f"Bearer {token}", "x-tenant-id": "tenant-a"}

    def _save(self, payload: dict[str, object]) -> tuple[int, dict[str, object]]:
        response = self.client.post("/api/v1/memory", headers=self.headers, json=payload)
        return response.status_code, response.json()

    def test_expense_event_requires_item_or_what_amount_currency(self) -> None:
        status_code, body = self._save(
            {
                "memory_type": "expense_event",
                "raw_text": "I spent 3",
                "structured_data": {"amount": 3.0},
                "confirmed": True,
            }
        )
        self.assertEqual(status_code, 422)
        self.assertEqual(body["error"]["code"], "memory.missing_required_fields")
        self.assertIn("item_or_what", body["error"]["details"]["missing_required_fields"])
        self.assertIn("currency", body["error"]["details"]["missing_required_fields"])

    def test_loan_event_requires_person_amount_currency_action(self) -> None:
        status_code, body = self._save(
            {
                "memory_type": "loan_event",
                "raw_text": "loan",
                "structured_data": {"amount": 50.0},
                "confirmed": True,
            }
        )
        self.assertEqual(status_code, 422)
        self.assertEqual(body["error"]["code"], "memory.missing_required_fields")
        missing = body["error"]["details"]["missing_required_fields"]
        self.assertIn("person_or_counterparty", missing)
        self.assertIn("currency", missing)
        self.assertIn("action", missing)

    def test_note_requires_what_or_content(self) -> None:
        status_code, body = self._save(
            {
                "memory_type": "note",
                "raw_text": "note",
                "structured_data": {},
                "confirmed": True,
            }
        )
        self.assertEqual(status_code, 422)
        self.assertEqual(body["error"]["code"], "memory.missing_required_fields")
        self.assertIn("what_or_content", body["error"]["details"]["missing_required_fields"])

    def test_document_requires_attachment_link(self) -> None:
        status_code, body = self._save(
            {
                "memory_type": "document",
                "raw_text": "invoice",
                "structured_data": {"content": "invoice doc"},
                "confirmed": True,
            }
        )
        self.assertEqual(status_code, 422)
        self.assertEqual(body["error"]["code"], "memory.missing_required_fields")
        self.assertIn("attachment_link", body["error"]["details"]["missing_required_fields"])


if __name__ == "__main__":
    unittest.main()
