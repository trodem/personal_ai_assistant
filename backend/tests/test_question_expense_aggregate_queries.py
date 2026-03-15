import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class QuestionExpenseAggregateQueriesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.tenant_id = f"tenant-expense-agg-{uuid4()}"
        token = build_dev_token(f"user-expense-agg-{uuid4()}", tenant_id=self.tenant_id)
        self.headers = {"Authorization": f"Bearer {token}", "x-tenant-id": self.tenant_id}

    def _save_expense(
        self,
        *,
        amount: float,
        item: str,
        currency: str = "CHF",
        category: str | None = None,
        when: str | None = None,
    ) -> str:
        structured_data: dict[str, object] = {"item": item, "amount": amount, "currency": currency}
        if category is not None:
            structured_data["category"] = category
        if when is not None:
            structured_data["when"] = when
        response = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "expense_event",
                "raw_text": f"I spent {amount} {currency} on {item}",
                "structured_data": structured_data,
                "confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["id"]

    def test_expense_aggregation_by_period_last_year(self) -> None:
        now = datetime.now(timezone.utc)
        last_year_date = now.replace(year=now.year - 1, month=5, day=10, hour=10, minute=0, second=0, microsecond=0)
        this_year_date = now.replace(month=5, day=11, hour=10, minute=0, second=0, microsecond=0)

        self._save_expense(amount=120.0, item="motorcycle", when=last_year_date.isoformat())
        self._save_expense(amount=50.0, item="motorcycle", when=this_year_date.isoformat())

        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend last year?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("120.00 CHF", payload["answer"])
        self.assertNotIn("170.00 CHF", payload["answer"])
        self.assertEqual(len(payload["source_memory_ids"]), 1)

    def test_expense_aggregation_by_object(self) -> None:
        self._save_expense(amount=200.0, item="motorcycle")
        self._save_expense(amount=40.0, item="groceries")

        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend on the motorcycle?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("200.00 CHF", payload["answer"])
        self.assertNotIn("240.00 CHF", payload["answer"])
        self.assertEqual(len(payload["source_memory_ids"]), 1)

    def test_expense_aggregation_by_category(self) -> None:
        current_month = datetime.now(timezone.utc).replace(day=5, hour=12, minute=0, second=0, microsecond=0)
        previous_month = (current_month - timedelta(days=35)).replace(day=5, hour=12, minute=0, second=0, microsecond=0)

        self._save_expense(
            amount=30.0,
            item="bus ticket",
            category="transport",
            when=current_month.isoformat(),
        )
        self._save_expense(
            amount=20.0,
            item="train ticket",
            category="transport",
            when=previous_month.isoformat(),
        )
        self._save_expense(
            amount=50.0,
            item="groceries",
            category="food",
            when=current_month.isoformat(),
        )

        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend in category transport this month?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("30.00 CHF", payload["answer"])
        self.assertNotIn("50.00 CHF", payload["answer"])
        self.assertEqual(len(payload["source_memory_ids"]), 1)


if __name__ == "__main__":
    unittest.main()
