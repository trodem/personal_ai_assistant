import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class QuestionLoanBalancesQueriesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.tenant_id = f"tenant-loan-balances-{uuid4()}"
        token = build_dev_token(f"user-loan-balances-{uuid4()}", tenant_id=self.tenant_id)
        self.headers = {"Authorization": f"Bearer {token}", "x-tenant-id": self.tenant_id}

    def _save_loan(self, *, person: str, amount: float, action: str, currency: str = "CHF") -> None:
        response = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "loan_event",
                "raw_text": f"{action} {amount} {currency} to {person}",
                "structured_data": {
                    "person": person,
                    "counterparty": person,
                    "amount": amount,
                    "currency": currency,
                    "action": action,
                },
                "confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_loan_balances_query_returns_who_owes_what(self) -> None:
        self._save_loan(person="Marco", amount=200.0, action="lend")
        self._save_loan(person="Anna", amount=50.0, action="borrow")

        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "Who owes what?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("Marco owes you 200.00 CHF", payload["answer"])
        self.assertIn("You owe Anna 50.00 CHF", payload["answer"])
        self.assertEqual(payload["confidence"], "high")
        self.assertEqual(len(payload["source_memory_ids"]), 2)

    def test_loan_balances_who_owes_me_filters_to_receivables(self) -> None:
        self._save_loan(person="Marco", amount=200.0, action="lend")
        self._save_loan(person="Anna", amount=50.0, action="borrow")

        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "Who still owes me money?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("Marco owes you 200.00 CHF", payload["answer"])
        self.assertNotIn("You owe Anna", payload["answer"])
        self.assertEqual(payload["confidence"], "high")

    def test_loan_balances_no_result_fallback(self) -> None:
        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "Who owes what?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["confidence"], "low")
        self.assertEqual(payload["source_memory_ids"], [])
        self.assertIn("add memory", payload["answer"].lower())


if __name__ == "__main__":
    unittest.main()
