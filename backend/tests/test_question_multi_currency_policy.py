import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class QuestionMultiCurrencyPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.tenant_id = f"tenant-multi-currency-{uuid4()}"
        token = build_dev_token(f"user-multi-currency-{uuid4()}", tenant_id=self.tenant_id)
        self.headers = {"Authorization": f"Bearer {token}", "x-tenant-id": self.tenant_id}

    def _save_expense(self, amount: float, item: str, currency: str) -> None:
        response = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "expense_event",
                "raw_text": f"I bought {item} for {amount} {currency}",
                "structured_data": {"item": item, "amount": amount, "currency": currency},
                "confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_text_query_separates_currency_totals_without_conversion(self) -> None:
        self._save_expense(10.0, "milk", "CHF")
        self._save_expense(25.5, "shoes", "EUR")

        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("10.00 CHF", payload["answer"])
        self.assertIn("25.50 EUR", payload["answer"])
        self.assertNotIn("35.50 CHF", payload["answer"])
        self.assertNotIn("35.50 EUR", payload["answer"])

    def test_text_query_applies_explicit_currency_filter(self) -> None:
        self._save_expense(10.0, "milk", "CHF")
        self._save_expense(25.5, "shoes", "EUR")

        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend in CHF?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("10.00 CHF", payload["answer"])
        self.assertNotIn("EUR", payload["answer"])

    def test_voice_query_preserves_multi_currency_separation(self) -> None:
        self._save_expense(7.0, "bread", "CHF")
        self._save_expense(3.0, "coffee", "USD")

        response = self.client.post(
            "/api/v1/voice/question",
            headers=self.headers,
            files={"audio": ("question.wav", b"How much did I spend?", "audio/wav")},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("7.00 CHF", payload["answer"])
        self.assertIn("3.00 USD", payload["answer"])
        self.assertNotIn("10.00 CHF", payload["answer"])


if __name__ == "__main__":
    unittest.main()
